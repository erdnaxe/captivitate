# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from .settings_local import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# Auth definition

PASSWORD_HASHERS = (
    'portail_captif.login.SSHAPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
)

AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'users',
    'portail_captif',
    'reversion',
    'django_prometheus'
)

MIDDLEWARE_CLASSES = (
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
)

ROOT_URLCONF = 'portail_captif.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates').replace('\\', '/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'portail_captif.context_processors.context_user',
            ],
        },
    },
]

WSGI_APPLICATION = 'portail_captif.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# django-bootstrap3 config dictionnary
BOOTSTRAP3 = {
    'jquery_url': '/static/js/jquery-2.2.4.min.js',
    'base_url': '/static/bootstrap/',
    'include_jquery': True,
}

BOOTSTRAP_BASE_URL = '/static/bootstrap/'

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(
        BASE_DIR,
        'static',
    ),
)

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')

PAGINATION_NUMBER = 25

PAGINATION_LARGE_NUMBER = 8

GENERIC_IPSET_COMMAND = "/sbin/ipset -q "
