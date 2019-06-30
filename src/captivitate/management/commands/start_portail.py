# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This script should run before the captive portal starts.
It fills iptables and activates routing.
"""

from django.core.management.base import BaseCommand

from .models import Machine, User
from .tools import restore_iptables, apply
from .apps import CaptivitateConfig


class Command(BaseCommand):
    help = 'Mets en place iptables et le set ip au démarage'

    def handle(self, *args, **options):
        # Create IP set
        apply(["sudo", "-n"] + CaptivitateConfig.generic_ipset_command.split() + [
            "create", CaptivitateConfig.IPSET_NAME, "hash:mac", "hashsize", "1024", "maxelem",
            "65536"])
        apply(["sudo", "-n"] + CaptivitateConfig.generic_ipset_command.split() + [
            "flush", CaptivitateConfig.IPSET_NAME])

        # Fill with authorized MACs
        active_users = User.objects.filter(is_active=True)
        all_machines = Machine.objects.filter(proprio__in=active_users)
        ipset = "%s\nCOMMIT\n" % '\n'.join(
            ["add %s %s" % (CaptivitateConfig.IPSET_NAME, str(m.mac_address)) for m in
             all_machines])
        command_to_execute = ["sudo", "-n"] + CaptivitateConfig.generic_ipset_command.split() + [
            "restore"]
        process = apply(command_to_execute)
        process.communicate(input=ipset.encode('utf-8'))

        # Restauration de l'iptables
        restore_iptables()

        # Activation du routage sur les bonnes if
        for interface in CaptivitateConfig.AUTORIZED_INTERFACES:
            apply(["sudo", "-n", "sysctl",
                   "net.ipv6.conf.%s.forwarding=1" % interface])
            apply(["sudo", "-n", "sysctl",
                   "net.ipv4.conf.%s.forwarding=1" % interface])
