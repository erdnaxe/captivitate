# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

"""
WSGI config for portail_captif project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys
from os.path import dirname

from django.core.wsgi import get_wsgi_application

# On démarre le système du portail

sys.path.append(dirname(dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portail_captif.settings")

application = get_wsgi_application()
