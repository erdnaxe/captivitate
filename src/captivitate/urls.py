# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from django.conf.urls import url

from . import views

app_name = 'captivitate'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new_user/$', views.new_user, name='new-user'),
    url(r'^capture/$', views.capture, name='capture'),
    url(r'^edit_info/(?P<userid>[0-9]+)$', views.edit_info, name='edit-info'),
    url(r'^reset_password/$', views.reset_password, name='reset-password'),
]
