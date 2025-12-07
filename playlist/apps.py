# from django.apps import AppConfig

# class PlaylistConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'playlist'

#     def ready(self):
#         from .seeds import seed_db
#         try:
#             seed_db()
#         except Exception as e:
#             print("Seeder error:", e)


from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class PlaylistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'playlist'

    def ready(self):
        # Only seed if the DB is ready
        try:
            from .seeds import seed_db
            from django.db import connections
            db_conn = connections['default']
            db_conn.ensure_connection()  # Make sure DB is reachable
            seed_db()
        except (OperationalError, ProgrammingError):
            # Tables not ready yet (migrations not applied)
            print("Seeder skipped: DB not ready")
        except Exception as e:
            print("Seeder error:", e)
