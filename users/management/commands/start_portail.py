# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Ce script est appellé avant le démarage du portail,
# il insère les bonnes règles dans l'iptables et active le routage

from django.core.management.base import BaseCommand

from portail_captif.settings import AUTORIZED_INTERFACES
from users.models import restore_iptables, create_ip_set, fill_ipset, apply


class Command(BaseCommand):
    help = 'Mets en place iptables et le set ip au démarage'

    def handle(self, *args, **options):
        # Creation de l'ipset
        create_ip_set()
        # Remplissage avec les macs autorisées
        fill_ipset()
        # Restauration de l'iptables
        restore_iptables()
        # Activation du routage sur les bonnes if
        for interface in AUTORIZED_INTERFACES:
            apply(["sudo", "-n", "sysctl",
                   "net.ipv6.conf.%s.forwarding=1" % interface])
            apply(["sudo", "-n", "sysctl",
                   "net.ipv4.conf.%s.forwarding=1" % interface])
