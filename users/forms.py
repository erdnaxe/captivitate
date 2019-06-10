# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.validators import MinLengthValidator
from django.forms import ModelForm

from .models import User


class PassForm(forms.Form):
    passwd1 = forms.CharField(
        label=u'Nouveau mot de passe', max_length=255,
        validators=[MinLengthValidator(8)],
        widget=forms.PasswordInput,
    )
    passwd2 = forms.CharField(
        label=u'Saisir à nouveau le mot de passe',
        max_length=255,
        validators=[MinLengthValidator(8)],
        widget=forms.PasswordInput,
    )


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput,
        validators=[MinLengthValidator(8)],
        max_length=255,
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput,
        validators=[MinLengthValidator(8)],
        max_length=255,
    )
    is_superuser = forms.BooleanField(label='is superuser')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        user.is_superuser = self.cleaned_data.get("is_superuser")
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()
    is_superuser = forms.BooleanField(label='is superuser', required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        print("User is admin : %s" % kwargs['instance'].is_superuser)
        self.initial['is_superuser'] = kwargs['instance'].is_superuser

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.is_superuser = self.cleaned_data.get("is_superuser")
        if commit:
            user.save()
        return user


class ResetPasswordForm(forms.Form):
    username = forms.CharField(label='username', max_length=255)
    email = forms.EmailField(max_length=255)


class BaseInfoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Prénom'
        self.fields['last_name'].label = 'Nom'

    class Meta:
        model = User
        fields = [
            'first_name',
            'username',
            'last_name',
            'email',
        ]


class InfoForm(BaseInfoForm):
    class Meta(BaseInfoForm.Meta):
        fields = [
            'first_name',
            'username',
            'comment',
            'last_name',
            'email',
            'is_superuser',
        ]
