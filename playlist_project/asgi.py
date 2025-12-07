"""
ASGI config for playlist_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playlist_project.settings')



django_asgi_app = get_asgi_application()

# For now we just use Django ASGI app (Channels could be plugged in later).
application = django_asgi_app
