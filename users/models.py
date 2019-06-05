# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

import datetime
import subprocess
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import ModelForm
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin
from macaddress.fields import MACAddressField

from portail_captif.settings import GENERIC_IPSET_COMMAND, IPSET_NAME, \
    REQ_EXPIRE_HRS, FORBIDEN_INTERFACES, SERVER_SELF_IP, AUTORIZED_INTERFACES, \
    PORTAIL_ACTIVE, INTERNAL_INTERFACE


def apply(cmd):
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)


def mac_from_ip(ip):
    cmd = ['/usr/sbin/arp', '-na', ip]
    p = apply(cmd)
    output, errors = p.communicate()
    if output is not None:
        mac_addr = output.decode().split()[3]
        return str(mac_addr)
    else:
        return None


def create_ip_set():
    command_to_execute = ["sudo", "-n"] + GENERIC_IPSET_COMMAND.split() + [
        "create", IPSET_NAME, "hash:mac", "hashsize", "1024", "maxelem",
        "65536"]
    apply(command_to_execute)
    command_to_execute = ["sudo", "-n"] + GENERIC_IPSET_COMMAND.split() + [
        "flush", IPSET_NAME]
    apply(command_to_execute)
    return


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
    return


class iptables:
    def __init__(self):
        self.nat = "\n*nat"
        self.mangle = "\n*mangle"
        self.filter = "\n*filter"

    def commit(self, chain):
        self.add(chain, "COMMIT\n")

    def add(self, chain, value):
        setattr(self, chain, getattr(self, chain) + "\n" + value)

    def init_filter(self, subchain, decision="ACCEPT"):
        self.add("filter", ":" + subchain + " " + decision)

    def init_nat(self, subchain, decision="ACCEPT"):
        self.add("nat", ":" + subchain + " " + decision)

    def init_mangle(self, subchain, decision="ACCEPT"):
        self.add("mangle", ":" + subchain + " " + decision)

    def jump(self, chain, subchainA, subchainB):
        self.add(chain, "-A " + subchainA + " -j " + subchainB)


def gen_filter(ipt):
    ipt.init_filter("INPUT")
    ipt.init_filter("FORWARD")
    ipt.init_filter("OUTPUT")
    for interface in FORBIDEN_INTERFACES:
        ipt.add("filter",
                "-A FORWARD -o %s -j REJECT --reject-with icmp-port-unreachable" % interface)
    ipt.add("filter",
            "-A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")
    for interface in AUTORIZED_INTERFACES:
        ipt.add("filter",
                "-A FORWARD -o %s -m set --match-set portail_captif src,dst -j ACCEPT" % interface)
        ipt.add("filter",
                "-A FORWARD -i %s -m set --match-set portail_captif src,dst -j ACCEPT" % interface)
    ipt.add("filter", "-A FORWARD -j REJECT")
    ipt.commit("filter")
    return ipt


def gen_nat(ipt, nat_active=True):
    ipt.init_nat("PREROUTING")
    ipt.init_nat("INPUT")
    ipt.init_nat("OUTPUT")
    ipt.init_nat("POSTROUTING")
    if nat_active:
        ipt.init_nat("CAPTIF", decision="-")
        ipt.jump("nat", "PREROUTING", "CAPTIF")
        ipt.jump("nat", "POSTROUTING", "MASQUERADE")
        if PORTAIL_ACTIVE:
            ipt.add("nat",
                    "-A CAPTIF -i %s -m set ! --match-set %s src,dst -j DNAT --to-destination %s" % (
                    INTERNAL_INTERFACE, IPSET_NAME, SERVER_SELF_IP))
        ipt.jump("nat", "CAPTIF", "RETURN")
    ipt.commit("nat")
    return ipt


def gen_mangle(ipt):
    ipt.init_mangle("PREROUTING")
    ipt.init_mangle("INPUT")
    ipt.init_mangle("FORWARD")
    ipt.init_mangle("OUTPUT")
    ipt.init_mangle("POSTROUTING")
    for interface in AUTORIZED_INTERFACES:
        ipt.add("mangle",
                """-A PREROUTING -i %s -m state --state NEW -j LOG --log-prefix "LOG_ALL " """ % interface)
    ipt.commit("mangle")
    return ipt


def restore_iptables():
    """ Restrore l'iptables pour la création du portail. Est appellé par root au démarage du serveur"""
    ipt = iptables()
    gen_mangle(ipt)
    gen_nat(ipt)
    gen_filter(ipt)
    global_chain = ipt.nat + ipt.filter + ipt.mangle
    command_to_execute = ["sudo", "-n", "/sbin/iptables-restore"]
    process = apply(command_to_execute)
    process.communicate(input=global_chain.encode('utf-8'))
    return


def disable_iptables():
    """ Insère une iptables minimaliste sans nat"""
    ipt = iptables()
    gen_mangle(ipt)
    gen_filter(ipt)
    gen_nat(ipt, nat_active=False)
    global_chain = ipt.nat + ipt.filter + ipt.mangle
    command_to_execute = ["sudo", "-n", "/sbin/iptables-restore"]
    process = apply(command_to_execute)
    process.communicate(input=global_chain.encode('utf-8'))
    return


class UserManager(BaseUserManager):
    def _create_user(self, pseudo, name, surname, email, password=None,
                     su=False):
        if not pseudo:
            raise ValueError('Users must have an username')

        user = self.model(
            pseudo=pseudo,
            name=name,
            surname=surname,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        if su:
            user.make_admin()
        return user

    def create_user(self, pseudo, name, surname, email, password=None):
        """
        Creates and saves a User with the given pseudo, name, surname, email,
        and password.
        """
        return self._create_user(pseudo, name, surname, email, password, False)

    def create_superuser(self, pseudo, name, surname, email, password):
        """
        Creates and saves a superuser with the given pseudo, name, surname,
        email, and password.
        """
        return self._create_user(pseudo, name, surname, email, password, True)


class User(ExportModelOperationsMixin('user'), AbstractBaseUser):
    PRETTY_NAME = "Utilisateurs"
    STATE_ACTIVE = 0
    STATE_DISABLED = 1
    STATE_ARCHIVE = 2
    STATES = (
        (0, 'STATE_ACTIVE'),
        (1, 'STATE_DISABLED'),
        (2, 'STATE_ARCHIVE'),
    )

    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    email = models.EmailField()
    state = models.IntegerField(choices=STATES, default=STATE_ACTIVE)
    pseudo = models.CharField(max_length=32, unique=True,
                              help_text="Doit contenir uniquement des lettres, chiffres, ou tirets. ")
    comment = models.CharField(help_text="Commentaire, promo", max_length=255,
                               blank=True)
    registered = models.DateTimeField(auto_now_add=True)
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'pseudo'
    REQUIRED_FIELDS = ['name', 'surname', 'email']

    objects = UserManager()

    @property
    def is_active(self):
        return self.state == self.STATE_ACTIVE

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_admin(self):
        return self.admin

    @is_admin.setter
    def is_admin(self, value):
        if value and not self.is_admin:
            self.make_admin()
        elif not value and self.is_admin:
            self.un_admin()

    def has_perms(self, perms, obj=None):
        for perm in perms:
            if perm == "admin":
                return self.is_admin
        return False

    def get_full_name(self):
        return '%s %s' % (self.name, self.surname)

    def get_short_name(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        # Simplest version again
        return True

    def make_admin(self):
        """ Make User admin """
        self.admin = True
        self.save()

    def un_admin(self):
        self.admin = False
        self.save()

    def machines(self):
        return Machine.objects.filter(proprio=self)

    def __str__(self):
        return self.name + " " + self.surname


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
def machine_post_save(sender, **kwargs):
    machine = kwargs['instance']
    machine.add_to_set()


@receiver(post_delete, sender=Machine)
def machine_post_delete(sender, **kwargs):
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


class BaseInfoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Prénom'
        self.fields['surname'].label = 'Nom'

    class Meta:
        model = User
        fields = [
            'name',
            'pseudo',
            'surname',
            'email',
        ]


class EditInfoForm(BaseInfoForm):
    class Meta(BaseInfoForm.Meta):
        fields = [
            'name',
            'pseudo',
            'surname',
            'comment',
            'email',
            'admin',
        ]


class InfoForm(BaseInfoForm):
    class Meta(BaseInfoForm.Meta):
        fields = [
            'name',
            'pseudo',
            'comment',
            'surname',
            'email',
            'admin',
        ]


class UserForm(EditInfoForm):
    class Meta(EditInfoForm.Meta):
        fields = '__all__'


class PasswordForm(ModelForm):
    class Meta:
        model = User
        fields = ['password']


class StateForm(ModelForm):
    class Meta:
        model = User
        fields = ['state']


class MachineForm(ModelForm):
    class Meta:
        model = Machine
        exclude = '__all__'
