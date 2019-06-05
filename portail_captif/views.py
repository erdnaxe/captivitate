# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from django.shortcuts import render
from django.template.context_processors import csrf


def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render(request, template, c)


def index(request):
    return form({}, 'portail_captif/index.html', request)
