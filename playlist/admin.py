
# Register your models here.
from django.contrib import admin
from .models import Track, PlaylistTrack

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "artist", "duration_seconds", "genre")

@admin.register(PlaylistTrack)
class PlaylistTrackAdmin(admin.ModelAdmin):
    list_display = ("id", "track", "position", "votes", "is_playing", "added_by")
    ordering = ("position",)
