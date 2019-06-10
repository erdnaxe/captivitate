# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django_prometheus import exports

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^', include('users.urls')),

    # Prometheus metrics
    url(r'^metrics$', exports.ExportToDjangoView,
        name='prometheus-django-metrics'),

    # Make Android detects that is it a captive portal
    url(r'^generate_204$', RedirectView.as_view(url='/')),
]
