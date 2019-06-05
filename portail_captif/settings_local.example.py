# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

SECRET_KEY = 'SUPER_SECRET'

DB_PASSWORD = 'SUPER_SECRET'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ADMINS = [('Example', 'rezo-admin@example.org')]

SERVER_EMAIL = 'no-reply@example.org'

# Obligatoire, liste des host autorisés
ALLOWED_HOSTS = ['test.example.org']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'portail_captif',
        'USER': 'portail_captif',
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',
    },
}

# Security settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_AGE = 60 * 60 * 3

# Association information

SITE_NAME = "Portail-captif"

ASSO_NAME = "Asso reseau"
ASSO_EMAIL = "tresorier@ecole.fr"

services_urls = {
    # Fill IT  : ex :  'gitlab': {
    #                           'url': 'https://gitlab.rezometz.org',
    #                           'logo': 'gitlab.png',
    #                           'description': 'Gitlab is cool 8-)'},
}

# Number of hours a token remains valid after having been created.  Numeric and string
# versions should have the same meaning.
REQ_EXPIRE_HRS = 48
REQ_EXPIRE_STR = '48 heures'

# Email `From` field
EMAIL_FROM = 'www-data@example.org'

EMAIL_HOST = 'smtp.example.org'

# Affchage des résultats
SEARCH_RESULT = 15

#### Réglages du portail

# Path de la commande ipset
GENERIC_IPSET_COMMAND = "/sbin/ipset"

# Nom de l'ipset utilisé
IPSET_NAME = "portail_captif"

### Interfaces où la sortie est interdite (ex vlan admin)
FORBIDEN_INTERFACES = ["ens19"]

### Ip où le trafic est redirigé
SERVER_SELF_IP = "192.168.0.1"

### Interfaces autorisées au routage
AUTORIZED_INTERFACES = ["ens18", "ens20"]

### Activation du portail obligatoire (redirection)
PORTAIL_ACTIVE = True

## Range ip du portail captif
CAPTIVE_IP_RANGE = "192.168.0.0/24"

## SSID du wifi portaul captif
CAPTIVE_WIFI = "Install-party"
