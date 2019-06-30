# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

import datetime
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from macaddress.fields import MACAddressField

from .apps import CaptivitateConfig
from .tools import apply


class User(ExportModelOperationsMixin('user'), AbstractUser):
    comment = models.CharField(
        verbose_name=_('comment'),
        max_length=255,
        blank=True,
    )
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']


class Machine(ExportModelOperationsMixin('machine'), models.Model):
    proprio = models.ForeignKey('User', on_delete=models.PROTECT)
    mac_address = MACAddressField(integer=False, unique=True)

    def add_to_set(self):
        command_to_execute = ["sudo",
                              "-n"] + CaptivitateConfig.generic_ipset_command.split() + [
                                 "add", CaptivitateConfig.ipset_name,
                                 str(self.mac_address)]
        apply(command_to_execute)

    def del_to_set(self):
        command_to_execute = ["sudo",
                              "-n"] + CaptivitateConfig.generic_ipset_command.split() + [
                                 "del", CaptivitateConfig.ipset_name,
                                 str(self.mac_address)]
        apply(command_to_execute)


@receiver(post_save, sender=Machine)
def machine_post_save(**kwargs):
    machine = kwargs['instance']
    machine.add_to_set()


@receiver(post_delete, sender=Machine)
def machine_post_delete(**kwargs):
    machine = kwargs['instance']
    machine.del_to_set()


class Request(models.Model):
    PASSWD = 'PW'
    EMAIL = 'EM'
    TYPE_CHOICES = (
        (PASSWD, 'Mot de passe'),
        (EMAIL, 'Email'),
    )
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    token = models.CharField(max_length=32)
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    expires_at = models.DateTimeField()

    def save(self, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() \
                              + datetime.timedelta(
                hours=CaptivitateConfig.request_expiry_hours)
        if not self.token:
            self.token = str(uuid.uuid4()).replace('-', '')  # remove hyphens
        super().save(**kwargs)
