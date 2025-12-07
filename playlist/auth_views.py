from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import AuthToken


def extract_token(request):
    """Extract token safely from Authorization header."""
    return request.headers.get("Authorization", "").replace("Token ", "").strip()


@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse({"error": {"code": "POST_REQUIRED"}}, status=400)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": {"code": "INVALID_JSON"}}, status=400)

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse({
            "error": {"code": "MISSING_FIELDS", "message": "Username and password required"}
        }, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": {"code": "USER_EXISTS"}}, status=400)

    user = User.objects.create_user(username=username, password=password)
    token = AuthToken.generate(user)

    return JsonResponse({"token": token, "username": username}, status=200)


@csrf_exempt
def login(request):
    if request.method != "POST":
        return JsonResponse({"error": {"code": "POST_REQUIRED"}}, status=400)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": {"code": "INVALID_JSON"}}, status=400)

    username = data.get("username")
    password = data.get("password")

    user = authenticate(username=username, password=password)
    if not user:
        return JsonResponse({"error": {"code": "INVALID_CREDENTIALS"}}, status=401)

    # Generate new token (old one deleted)
    token = AuthToken.generate(user)
    return JsonResponse({"token": token, "username": username}, status=200)


def me(request):
    token = extract_token(request)
    if not token:
        return JsonResponse({"error": {"code": "NO_TOKEN"}}, status=401)

    tokens = AuthToken.objects.filter(key=token)

    if not tokens.exists():
        return JsonResponse({"error": {"code": "INVALID_TOKEN"}}, status=401)

    if tokens.count() > 1:
        first = tokens.first()
        tokens.exclude(pk=first.pk).delete()
        return JsonResponse({"username": first.user.username})

    return JsonResponse({"username": tokens.first().user.username})
