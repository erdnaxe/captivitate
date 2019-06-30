# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2016-2019 by Cr@ns
# SPDX-License-Identifier: GPL-2.0-or-later
# This file is part of captivitate.

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from django_prometheus import exports

urlpatterns = [
    url(r'^', include('users.urls')),

    # Prometheus metrics
    url(r'^metrics$', exports.ExportToDjangoView,
        name='prometheus-django-metrics'),

    # Make Android detects that is it a captive portal
    url(r'^generate_204$', RedirectView.as_view(url='/')),

    # Include Django Contrib and Core routers
    # admin/login/ is redirected to the non-admin login page
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/profile/',
        RedirectView.as_view(pattern_name='users:index')),
    url(r'^admin/login/', RedirectView.as_view(pattern_name='login')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
]
