# playlist/urls.py
from django.urls import path
from django.http import HttpResponse
from . import views
from . import auth_views

urlpatterns = [
    # AUTH
    path("api/auth/login", auth_views.login),
    path("api/auth/register", auth_views.register),
    path("api/auth/me", auth_views.me),

    # root
    path("", lambda request: HttpResponse("Django backend is running.")),

    # TRACKS
    path("api/tracks", views.api_tracks),

    # PLAYLIST
    path("api/playlist", views.api_playlist),
    path("api/playlist/add", views.api_add_to_playlist),
    path("api/playlist/<str:playlist_id>/update", views.api_update_playlist),
    path("api/playlist/<str:playlist_id>/vote", views.api_vote),
    path("api/playlist/<str:playlist_id>/delete", views.api_delete),

    # SEED
    # path("admin/seed", views.seed_endpoint),
    path("api/admin/seed", views.seed_endpoint),


    # SSE stream
    path("api/stream", views.stream_events),


]
