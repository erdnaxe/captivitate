# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

import datetime
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin
from macaddress.fields import MACAddressField

from portail_captif.settings import GENERIC_IPSET_COMMAND, IPSET_NAME, \
    REQ_EXPIRE_HRS
from .tools import apply


class UserManager(DjangoUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Creates and saves an user
        """
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Creates and saves a superuser
        """
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, email, password, **extra_fields)


class User(ExportModelOperationsMixin('user'), AbstractBaseUser):
    # PermissionsMixin TODO
    PRETTY_NAME = "Utilisateurs"
    STATE_ACTIVE = 0
    STATE_DISABLED = 1
    STATE_ARCHIVE = 2
    STATES = (
        (0, 'STATE_ACTIVE'),
        (1, 'STATE_DISABLED'),
        (2, 'STATE_ARCHIVE'),
    )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    state = models.IntegerField(choices=STATES, default=STATE_ACTIVE)
    username = models.CharField(max_length=32, unique=True,
                                help_text="Doit contenir uniquement des lettres, chiffres, ou tirets. ")
    comment = models.CharField(help_text="Commentaire, promo", max_length=255,
                               blank=True)
    registered = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    objects = UserManager()

    @property
    def is_active(self):
        return self.state == self.STATE_ACTIVE

    @property
    def is_staff(self):
        return self.is_superuser

    def has_perms(self, perms, obj=None):
        for perm in perms:
            if perm == "admin":
                return self.is_superuser
        return False

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def machines(self):
        return Machine.objects.filter(proprio=self)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Machine(ExportModelOperationsMixin('machine'), models.Model):
    proprio = models.ForeignKey('User', on_delete=models.PROTECT)
    mac_address = MACAddressField(integer=False, unique=True)

    def add_to_set(self):
        command_to_execute = ["sudo", "-n"] + GENERIC_IPSET_COMMAND.split() + [
            "add", IPSET_NAME, str(self.mac_address)]
        apply(command_to_execute)

    def del_to_set(self):
        command_to_execute = ["sudo", "-n"] + GENERIC_IPSET_COMMAND.split() + [
            "del", IPSET_NAME, str(self.mac_address)]
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
                              + datetime.timedelta(hours=REQ_EXPIRE_HRS)
        if not self.token:
            self.token = str(uuid.uuid4()).replace('-', '')  # remove hyphens
        super().save(**kwargs)


def fill_ipset():
    all_machines = Machine.objects.filter(
        proprio__in=User.objects.filter(state=User.STATE_ACTIVE))
    ipset = "%s\nCOMMIT\n" % '\n'.join(
        ["add %s %s" % (IPSET_NAME, str(machine.mac_address)) for machine in
         all_machines])
    command_to_execute = ["sudo", "-n"] + GENERIC_IPSET_COMMAND.split() + [
        "restore"]
    process = apply(command_to_execute)
    process.communicate(input=ipset.encode('utf-8'))
