import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from whitenoise.django import DjangoWhiteNoise  # Must be after DJANGO_SETTINGS_MODULE is defined

application = DjangoWhiteNoise(get_wsgi_application())
