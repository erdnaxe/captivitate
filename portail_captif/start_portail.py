# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Ce script est appellé avant le démarage du portail, il insère les bonnes règles
# dans l'iptables et active le routage

import os, sys

from django.core.wsgi import get_wsgi_application
from os.path import dirname

proj_path = "/var/www/portail_captif/"
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portail_captif.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

from users.models import restore_iptables, create_ip_set, fill_ipset, apply
from portail_captif.settings import AUTORIZED_INTERFACES


application = get_wsgi_application()

# Creation de l'ipset
create_ip_set()

# Remplissage avec les macs autorisées
fill_ipset()

# Restauration de l'iptables
restore_iptables()
# Activation du routage sur les bonnes if
for interface in AUTORIZED_INTERFACES:
    apply("echo 1 > /proc/sys/net/ipv6/conf/%s/forwarding" % interface)
    apply("echo 1 > /proc/sys/net/ipv4/conf/%s/forwarding" % interface)


