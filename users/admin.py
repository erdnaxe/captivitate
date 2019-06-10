# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from reversion.admin import VersionAdmin
from django.utils.translation import ugettext_lazy as _

from .forms import UserAdminForm, UserCreationAdminForm
from .models import User, Machine, Request


class RequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created_at', 'expires_at')


class MachineAdmin(VersionAdmin):
    list_display = ('mac_address', 'proprio')
    search_fields = ('mac_address', 'proprio__username')


class UserAdmin(VersionAdmin, BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminForm
    add_form = UserCreationAdminForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'comment')}),
        (_('Permissions'), {'fields': ('is_superuser', 'state')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name', 'last_name', 'email', 'is_superuser', 'password1',
                'password2')}
         ),
    )
    filter_horizontal = ()

    # TODO(erdnaxe): édition date inscription, changement mdp


admin.site.register(Machine, MachineAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Request, RequestAdmin)
# Now register the new UserAdmin...
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
