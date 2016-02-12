"""
Django settings for gourmand project.
"""
import os

import environ

env = environ.Env(DEBUG=(bool, False), ALLOWED_HOSTS=(list, []), OPBEAT=(dict, {}))

BASE_DIR = environ.Path(__file__) - 2


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')


# Application definition

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'django_extensions',
    'bootstrap3',
    'debug_toolbar',
    'django_q',
    'opbeat.contrib.django',
    'hijack',
    'compat',
)

LOCAL_APPS = (
    'feeds',
    'subscriptions',
    'branding',
    'tools',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'async_messages.middleware.AsyncMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)


def show_toolbar(request):
    if DEBUG or request.user.is_superuser:
        debug = request.GET.get("debug", None)
        if debug == "on":
            request.session["debug"] = True
        elif debug == "off" and "debug" in request.session:
            del request.session["debug"]
        return "debug" in request.session


DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL':'',
    'RENDER_PANELS': True,
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.show_toolbar',
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (BASE_DIR('templates'),),
        'OPTIONS': {
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

if DEBUG:  # For quicker development, reload template changes w/o restarting server
    TEMPLATES[0]['OPTIONS'].pop('loaders', None)
    TEMPLATES[0]['APP_DIRS'] = True

DEBUG_TOOLBAR_PATCH_SETTINGS = False

WSGI_APPLICATION = 'config.wsgi.application'

# django-hijack
HIJACK_USE_BOOTSTRAP = True

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': env.db(),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASES['default']['CONN_MAX_AGE'] = 120


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
STATIC_URL = '/static/'
BASE_STATIC = BASE_DIR.path('static')

STATICFILES_DIRS = (
    BASE_STATIC('static_files'),
)
STATIC_ROOT = BASE_STATIC('collected_files')
WHITENOISE_ROOT = BASE_STATIC('root_files')


# Authentication
LOGIN_REDIRECT_URL = 'reader'


# Bootstrap3 settings - http://django-bootstrap3.readthedocs.org/en/latest/settings.html
BOOTSTRAP3 = {'include_jquery': True}


# Cache settings
CACHES = {
    'default': env.cache(),
}

# Django-Q settings
Q_CLUSTER = {
    'name': 'DjangoORM',
    'orm': 'default',
    'workers': 1 + os.cpu_count() * 2,
    'retry': 600,
    'timeout': 300,
    'catch_up': False,  # Run missed scheduled tasks only once
}

# Opbeat
OPBEAT = env('OPBEAT')
