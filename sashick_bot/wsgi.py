"""
WSGI config for sashick_bot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

if os.environ.get('DJANGO_ENV') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sashick_bot.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sashick_bot.settings')

application = get_wsgi_application()
