from .models import Track, PlaylistTrack
from django.utils import timezone
import random

SAMPLE_TRACKS = [
    ("Bohemian Rhapsody","Queen","A Night at the Opera",355,"Rock"),
    ("Imagine","John Lennon","Imagine",183,"Pop"),
    ("Billie Jean","Michael Jackson","Thriller",294,"Pop"),
    ("Take Five","Dave Brubeck","Time Out",324,"Jazz"),
    ("Clair de Lune","Debussy","Suite bergamasque",300,"Classical"),
    ("Heroes","David Bowie","Heroes",369,"Rock"),
    ("Around the World","Daft Punk","Homework",429,"Electronic"),
    ("One More Time","Daft Punk","Discovery",320,"Electronic"),
    ("Smells Like Teen Spirit","Nirvana","Nevermind",301,"Rock"),
    ("Lose Yourself","Eminem","8 Mile",326,"Hip-Hop"),
    ("Shape of You","Ed Sheeran","Divide",233,"Pop"),
    ("Stairway to Heaven","Led Zeppelin","Untitled",482,"Rock"),
    ("Hallelujah","Jeff Buckley","Grace",370,"Folk"),
    ("Comfortably Numb","Pink Floyd","The Wall",385,"Rock"),
]

# def seed_db():
#     # Create tracks
#     if Track.objects.count() == 0:
#         for t in SAMPLE_TRACKS:
#             Track.objects.create(
#                 title=t[0],
#                 artist=t[1],
#                 album=t[2],
#                 duration_seconds=t[3],
#                 genre=t[4]
#             )

#     # Add all tracks to playlist
#     if PlaylistTrack.objects.count() == 0:
#         tracks = list(Track.objects.all())  # use all tracks

#         position = 1.0
#         for i, tr in enumerate(tracks):
#             pt = PlaylistTrack.objects.create(
#                 track=tr,
#                 position=position,
#                 votes=random.randint(-2, 10),
#                 added_by=f"Seeder{i}"
#             )

#             if i == 0:
#                 pt.is_playing = True
#                 pt.played_at = timezone.now()
#                 pt.save()

#             position += 1.0


def seed_db():
    from django.db.utils import OperationalError
    try:
        if Track.objects.count() == 0:
            for t in SAMPLE_TRACKS:
                Track.objects.create(
                    title=t[0],
                    artist=t[1],
                    album=t[2],
                    duration_seconds=t[3],
                    genre=t[4]
                )

        if PlaylistTrack.objects.count() == 0:
            tracks = list(Track.objects.all()[:8])
            position = 1.0
            for i, tr in enumerate(tracks):
                pt = PlaylistTrack.objects.create(
                    track=tr,
                    position=position,
                    votes=random.randint(-2, 10),
                    added_by=f"Seeder{i}"
                )
                if i == 0:
                    pt.is_playing = True
                    pt.played_at = timezone.now()
                    pt.save()
                position += 1.0
    except OperationalError:
        print("Seeder skipped: DB tables not ready yet")
