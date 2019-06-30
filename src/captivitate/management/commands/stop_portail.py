# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This script should run after the captive portal stops.
It empties iptables and deactivates routing.
"""

from django.core.management.base import BaseCommand

from .tools import disable_iptables, apply
from .apps import CaptivitateConfig


class Command(BaseCommand):
    help = 'Mets en place iptables et le set ip au démarage'

    def handle(self, *args, **options):
        # Destruction de l'iptables
        disable_iptables()

        # Desactivation du routage sur les bonnes if
        for interface in CaptivitateConfig.AUTORIZED_INTERFACES:
            apply(["sudo", "-n", "sysctl",
                   "net.ipv6.conf.%s.forwarding=0" % interface])
            apply(["sudo", "-n", "sysctl",
                   "net.ipv4.conf.%s.forwarding=0" % interface])
