# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django_prometheus import exports

from .views import index

urlpatterns = [
    url(r'^$', index),
    url('^logout/', auth_views.logout, {'next_page': '/'}),
    url('^', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^metrics$', exports.ExportToDjangoView,
        name='prometheus-django-metrics'),

    # Make Android detects that is it a captive portal
    url(r'^generate_204$', RedirectView.as_view(url='/')),
]
