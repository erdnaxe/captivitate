from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CaptivitateConfig(AppConfig):
    name = 'captivitate'
    verbose_name = _('captivitate')

    generic_ipset_command = "/sbin/ipset"
    ipset_name = "portail_captif"

    # Number of hours a token remains valid after having been created.
    # Numeric and string versions should have the same meaning.
    request_expiry_hours = 48
    request_expiry_string = '48 heures'

    # TODO: should be removed
    default_from_email = 'www-data@example.org'
    SITE_NAME = "Portail captif"

    # Association information
    ASSO_NAME = "Asso reseau"
    ASSO_EMAIL = "tresorier@ecole.fr"

    # IP range
    CAPTIVE_IP_RANGE = "192.168.0.0/24"

    # WiFi SSID
    CAPTIVE_WIFI = "Install-party"

    # Interfaces où la sortie est interdite (ex vlan admin)
    FORBIDEN_INTERFACES = ["ens19"]

    # Interface Interne
    INTERNAL_INTERFACE = "ens20"

    # Interfaces autorisées au routage
    OUT_INTERFACE = "ens21"

    # Interfaces autorisées au routage
    AUTORIZED_INTERFACES = [INTERNAL_INTERFACE] + [OUT_INTERFACE]

    # Ip où le trafic est redirigé
    SERVER_SELF_IP = "192.168.0.1"

    # Activation du portail obligatoire (redirection)
    PORTAIL_ACTIVE = True
