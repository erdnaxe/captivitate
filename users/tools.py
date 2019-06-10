# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

import subprocess

from portail_captif.settings import IPSET_NAME, \
    FORBIDEN_INTERFACES, SERVER_SELF_IP, AUTORIZED_INTERFACES, \
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
