# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin

from .models import User, Machine, Request


class RequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created_at', 'expires_at')


class MachineAdmin(VersionAdmin):
    list_display = ('mac_address', 'proprio')
    search_fields = ('mac_address', 'proprio__username')


class UserAdmin(VersionAdmin, BaseUserAdmin):
    # Add comment in fieldset
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email',
                                         'comment')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(Machine, MachineAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Request, RequestAdmin)
# Now register the new UserAdmin...
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
