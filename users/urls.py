# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from django.conf.urls import url

from . import views

app_name = 'users'
urlpatterns = [
    url(r'^new_user/$', views.new_user, name='new-user'),
    url(r'^capture/$', views.capture, name='capture'),
    url(r'^edit_info/(?P<userid>[0-9]+)$', views.edit_info, name='edit-info'),
    url(r'^state/(?P<userid>[0-9]+)$', views.state, name='state'),
    url(r'^password/(?P<userid>[0-9]+)$', views.password, name='password'),
    url(r'^profil/(?P<userid>[0-9]+)$', views.profil, name='profil'),
    url(r'^mon_profil/$', views.mon_profil, name='mon-profil'),
    url(r'^process/(?P<token>[a-z0-9]{32})/$', views.process, name='process'),
    url(r'^reset_password/$', views.reset_password, name='reset-password'),
    url(r'^history/(?P<object>user)/(?P<id>[0-9]+)$', views.history,
        name='history'),
    url(r'^history/(?P<object>machines)/(?P<id>[0-9]+)$', views.history,
        name='history'),
    url(r'^$', views.index, name='index'),
]
