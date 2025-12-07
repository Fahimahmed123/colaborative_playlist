# playlist/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import F
import json

from .models import Track, PlaylistTrack, AuthToken
from .event_broker import broker

# ============================================================
# TOKEN AUTH HELPER
# ============================================================

def get_user_from_token(request):
    token = request.headers.get("Authorization", "").replace("Token ", "").strip()
    if not token:
        return None
    tokens = AuthToken.objects.filter(key=token)
    if not tokens.exists():
        return None
    if tokens.count() > 1:
        first = tokens.first()
        tokens.exclude(pk=first.pk).delete()
        return first.user
    return tokens.first().user

# ============================================================
# POSITION ALGORITHM
# ============================================================

def calculate_position(prev_position, next_position):
    if prev_position is None and next_position is None:
        return 1.0
    if prev_position is None:
        return next_position - 1
    if next_position is None:
        return prev_position + 1
    return (prev_position + next_position) / 2

# ============================================================
# HELPERS
# ============================================================

def playlist_ordered():
    return PlaylistTrack.objects.select_related("track").order_by("position")

def playlist_as_list():
    return [p.as_dict() for p in playlist_ordered()]

# ============================================================
# PUBLIC API: TRACKS & PLAYLIST
# ============================================================

def api_tracks(request):
    tracks = Track.objects.all()
    return JsonResponse([t.as_dict() for t in tracks], safe=False)

def api_playlist(request):
    return JsonResponse(playlist_as_list(), safe=False)

# ============================================================
# ADD TRACK
# ============================================================

@csrf_exempt
def api_add_to_playlist(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    user = get_user_from_token(request)
    if not user:
        return JsonResponse({"error": "AUTH_REQUIRED"}, status=401)

    try:
        payload = json.loads(request.body.decode())
    except Exception:
        return HttpResponseBadRequest(json.dumps({"error": "INVALID_JSON"}), content_type="application/json")

    track_id = payload.get("track_id")
    try:
        track = Track.objects.get(id=track_id)
    except Track.DoesNotExist:
        return HttpResponseNotFound(json.dumps({"error": {"code": "TRACK_NOT_FOUND"}}), content_type="application/json")

    # server-side duplicate prevention
    if PlaylistTrack.objects.filter(track=track).exists():
        return HttpResponseBadRequest(
            json.dumps({
                "error": {
                    "code": "DUPLICATE_TRACK",
                    "message": "This track is already in the playlist",
                    "details": {"track_id": track_id},
                }
            }), content_type="application/json"
        )

    last = PlaylistTrack.objects.order_by("-position").first()
    pos = calculate_position(last.position if last else None, None)

    item = PlaylistTrack.objects.create(
        track=track,
        position=pos,
        votes=payload.get("votes", 0),
        added_by=user.username,
        added_at=timezone.now()
    )

    obj = item.as_dict()
    broker.publish({"type": "track.added", "item": obj})
    return JsonResponse(obj, status=201)

# ============================================================
# UPDATE ITEM (position / play)
# ============================================================

@csrf_exempt
def api_update_playlist(request, playlist_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    user = get_user_from_token(request)
    if not user:
        return JsonResponse({"error": "AUTH_REQUIRED"}, status=401)

    try:
        payload = json.loads(request.body.decode())
    except Exception:
        return HttpResponseBadRequest(json.dumps({"error": "INVALID_JSON"}), content_type="application/json")

    new_pos = payload.get("position")
    playing_flag = payload.get("is_playing")

    try:
        item = PlaylistTrack.objects.get(id=playlist_id)
    except PlaylistTrack.DoesNotExist:
        return HttpResponseNotFound(json.dumps({"error": "NOT_FOUND"}), content_type="application/json")

    # enforce single now-playing
    if playing_flag is not None:
        if playing_flag:
            PlaylistTrack.objects.filter(is_playing=True).exclude(pk=item.pk).update(is_playing=False, played_at=None)
            item.is_playing = True
            item.played_at = timezone.now()
        else:
            item.is_playing = False
            item.played_at = None

    if new_pos is not None:
        item.position = float(new_pos)

    item.save()
    broker.publish({"type": "track.moved" if new_pos is not None else "track.playing", "item": item.as_dict()})
    return JsonResponse(item.as_dict())

# ============================================================
# VOTE
# ============================================================

@csrf_exempt
def api_vote(request, playlist_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    user = get_user_from_token(request)
    if not user:
        return JsonResponse({"error": "AUTH_REQUIRED"}, status=401)

    try:
        payload = json.loads(request.body.decode())
    except Exception:
        return HttpResponseBadRequest(json.dumps({"error": "INVALID_JSON"}), content_type="application/json")

    direction = payload.get("direction")
    try:
        item = PlaylistTrack.objects.get(id=playlist_id)
    except PlaylistTrack.DoesNotExist:
        return HttpResponseNotFound(json.dumps({"error": "NOT_FOUND"}), content_type="application/json")

    if direction == "up":
        item.votes = F("votes") + 1
    elif direction == "down":
        item.votes = F("votes") - 1
    else:
        return HttpResponseBadRequest(json.dumps({"error": "INVALID_DIRECTION"}), content_type="application/json")

    item.save()
    item.refresh_from_db()
    broker.publish({"type": "track.voted", "item": item.as_dict()})
    return JsonResponse({"id": item.id, "votes": item.votes})

# ============================================================
# DELETE
# ============================================================

@csrf_exempt
def api_delete(request, playlist_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    user = get_user_from_token(request)
    if not user:
        return JsonResponse({"error": "AUTH_REQUIRED"}, status=401)

    try:
        item = PlaylistTrack.objects.get(id=playlist_id)
    except PlaylistTrack.DoesNotExist:
        return HttpResponseNotFound(json.dumps({"error": "NOT_FOUND"}), content_type="application/json")

    item.delete()
    broker.publish({"type": "track.removed", "id": playlist_id})
    return JsonResponse({}, status=204, safe=False)

# ============================================================
# SSE STREAM
# ============================================================

def stream_events(request):
    """
    SSE endpoint: /api/stream
    Optional ?last=<index> to attempt resume.
    """
    try:
        last = int(request.GET.get("last", 0))
    except Exception:
        last = 0

    def event_stream():
        for idx, payload in broker.listen(last_index=last):
            s = f"id: {idx}\n"
            s += f"event: message\n"
            s += f"data: {payload}\n\n"
            yield s

    resp = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    resp['Cache-Control'] = 'no-cache'
    return resp

# ============================================================
# SEED
# ============================================================

def seed_endpoint(request):
    from .seeds import seed_db
    seed_db()
    return HttpResponse("seeded")
