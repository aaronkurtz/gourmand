"""
Django settings for gourmand project.
"""

import environ

env = environ.Env(DEBUG=(bool, False), ALLOWED_HOSTS=(list, []))

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
)

LOCAL_APPS = (
    'feeds',
    'subscriptions',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'async_messages.middleware.AsyncMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (BASE_DIR('templates'),),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': env.db(),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

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
    'retry': 600,
    'timeout': 300,
}
