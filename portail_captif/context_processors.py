# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from .settings import SITE_NAME


def context_user(request):
    user = request.user
    is_admin = user.is_admin if hasattr(user, 'is_admin') else False
    return {
        'is_admin': is_admin,
        'request_user': user,
        'site_name': SITE_NAME,
    }
