# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from django.conf.urls import url

from . import views

app_name = 'users'
urlpatterns = [
    url(r'^new_user/$', views.new_user, name='new-user'),
    url(r'^capture/$', views.capture, name='capture'),
    url(r'^edit_info/(?P<userid>[0-9]+)$', views.edit_info, name='edit-info'),
    url(r'^password/(?P<userid>[0-9]+)$', views.password, name='password'),
    url(r'^$', views.profile, name='profile'),
    url(r'^process/(?P<token>[a-z0-9]{32})/$', views.process, name='process'),
    url(r'^reset_password/$', views.reset_password, name='reset-password'),
]
