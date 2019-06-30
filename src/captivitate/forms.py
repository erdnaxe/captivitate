# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import ModelForm

from .models import User


class ResetPasswordForm(forms.Form):
    username = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Envoyer'))


class BaseInfoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Envoyer'))

    class Meta:
        model = User
        fields = [
            'first_name',
            'username',
            'last_name',
            'email',
        ]
        help_texts = {
            'email': 'Le mail est utilisé pour initialiser le compte.',
        }
