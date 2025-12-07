from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import User


def gen_track_id():
    return f"track-{uuid.uuid4().hex[:8]}"


def gen_playlist_id():
    return f"playlist-{uuid.uuid4().hex[:8]}"


# ============================================================
# TRACK LIBRARY
# ============================================================

class Track(models.Model):
    id = models.CharField(
        max_length=40,
        primary_key=True,
        default=gen_track_id,
    )
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    album = models.CharField(max_length=200, blank=True, null=True)
    duration_seconds = models.IntegerField()
    genre = models.CharField(max_length=100, blank=True, null=True)
    cover_url = models.CharField(max_length=500, blank=True, null=True)

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration_seconds": self.duration_seconds,
            "genre": self.genre,
            "cover_url": self.cover_url,
        }


# ============================================================
# PLAYLIST
# ============================================================

class PlaylistTrack(models.Model):
    id = models.CharField(
        max_length=40,
        primary_key=True,
        default=gen_playlist_id,
    )
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    position = models.FloatField(db_index=True)
    votes = models.IntegerField(default=0)
    added_by = models.CharField(max_length=100, default="Anonymous")
    added_at = models.DateTimeField(default=timezone.now)
    is_playing = models.BooleanField(default=False)
    played_at = models.DateTimeField(blank=True, null=True)

    def as_dict(self):
        return {
            "id": self.id,
            "track_id": self.track.id,
            "track": self.track.as_dict(),
            "position": self.position,
            "votes": self.votes,
            "added_by": self.added_by,
            "is_playing": self.is_playing,
            "added_at": self.added_at.isoformat(),
        }


# ============================================================
# TOKEN AUTH (SAFE VERSION)
# ============================================================

# class AuthToken(models.Model):
#     key = models.CharField(max_length=64, primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)


#     @staticmethod
#     def generate(user):
#         # Get all tokens for this user
#         tokens = AuthToken.objects.filter(user=user)

#         if tokens.count() > 1:
#             # Keep the first, delete the rest
#             first = tokens.first()
#             tokens.exclude(pk=first.pk).delete()
#             token_obj = first
#         elif tokens.count() == 1:
#             token_obj = tokens.first()
#         else:
#             # No existing token → create one
#             token_obj = AuthToken(key=uuid.uuid4().hex, user=user)

#         # Refresh or set key
#         token_obj.key = uuid.uuid4().hex
#         token_obj.save()

#         return token_obj.key

#     def __str__(self):
#         return f"Token({self.user.username})"
    

    
class AuthToken(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @staticmethod
    def generate(user):
        # Get all tokens for this user
        tokens = AuthToken.objects.filter(user=user)

        if tokens.count() > 1:
            # Keep only first token
            first = tokens.first()
            tokens.exclude(pk=first.pk).delete()
            token_obj = first

        elif tokens.count() == 1:
            token_obj = tokens.first()

        else:
            token_obj = AuthToken(key=uuid.uuid4().hex, user=user)

        # Refresh token key to rotate
        token_obj.key = uuid.uuid4().hex
        token_obj.save()

        return token_obj.key

    def __str__(self):
        return f"Token({self.user.username})"
