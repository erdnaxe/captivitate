# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

import ipaddress

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from reversion import revisions as reversion

from .apps import CaptivitateConfig
from .forms import ResetPasswordForm, BaseInfoForm
from .models import User, Machine
from .tools import mac_from_ip


def form(ctx, template, request):
    ctx.update(csrf(request))
    return render(request, template, ctx)


def index(request):
    """
    Show logged in user profile or index page
    """
    if request.user.is_authenticated:
        try:
            users = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
            raise Http404
        machines_list = Machine.objects.filter(proprio=users)
        return render(
            request,
            'captivitate/profile.html',
            {
                'user': users,
                'machines_list': machines_list,
            }
        )
    else:
        return render(request, 'captivitate/index.html', {})


def new_user(request):
    """
    View to create a new user
    """
    user = BaseInfoForm(request.POST or None)
    if user.is_valid():
        user = user.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            user.save()
            reversion.set_comment("Création")

        # Virtually fill the password reset form from Django Contrib Auth
        # TODO doesn't work
        password_reset = PasswordResetForm(data={'email': user.email})
        if password_reset.is_valid():
            password_reset.save(
                request=request,
                use_https=request.is_secure(),
            )
            messages.success(request, _("User successfully created! "
                                        "A password initialisation email "
                                        "was sent."))
            return redirect(reverse('index'))
        else:
            messages.error(request, _("The email is invalid."))

        # Try to register the current MAC address
        capture_mac(request, user)

        return redirect("/")
    return form({'userform': user}, 'captivitate/user.html', request)


@login_required
def edit_info(request, userid):
    """
    View to edit an user
    """
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/")
    if not request.user.is_superuser and user != request.user:
        messages.error(request,
                       "Vous ne pouvez pas modifier un autre user que vous sans droit admin")
        return redirect("/")
    user = BaseInfoForm(request.POST or None, instance=user)
    if user.is_valid():
        with transaction.atomic(), reversion.create_revision():
            user.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in user.changed_data))
        messages.success(request, "L'user a bien été modifié")
        return redirect("/")
    return form({'userform': user}, 'captivitate/user.html', request)


def get_ip(request):
    """
    Returns the IP of the request, accounting for the possibility of being
    behind a proxy.
    """
    ip = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if ip:
        # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
        ip = ip.split(", ")[0]
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip


def capture_mac(request, users, verbose=True):
    remote_ip = get_ip(request)
    if remote_ip and ipaddress.ip_address(remote_ip) in ipaddress.ip_network(
            CaptivitateConfig.CAPTIVE_IP_RANGE):
        mac_addr = mac_from_ip(remote_ip)
        if mac_addr:
            machine = Machine()
            machine.proprio = users
            machine.mac_address = str(mac_addr)
            try:
                with transaction.atomic(), reversion.create_revision():
                    machine.save()
                    reversion.set_comment("Enregistrement de la machine")
            except:
                if verbose:
                    messages.error(request,
                                   "Assurez-vous que la machine n'est pas déjà enregistrée")
        else:
            if verbose:
                messages.error(request, "Impossible d'enregistrer la machine")
    else:
        if verbose:
            messages.error(request,
                           "Merci de vous connecter sur le réseau du portail captif pour capturer la machine (WiFi %s)" % CaptivitateConfig.CAPTIVE_WIFI)


def capture_mac_afterlogin(sender, user, request, **kwargs):
    capture_mac(request, user, verbose=False)


# On récupère la mac après le login
user_logged_in.connect(capture_mac_afterlogin)


@login_required
def capture(request):
    userid = str(request.user.id)
    try:
        users = User.objects.get(pk=userid)
    except User.DoesNotExist:
        raise Http404
    capture_mac(request, users)
    return redirect("/")


def reset_password(request):
    """
    Ask the username and the email to reset the password
    """
    userform = ResetPasswordForm(request.POST or None)
    if userform.is_valid():
        user = None
        try:
            user = User.objects.get(
                username=userform.cleaned_data['username'],
                email=userform.cleaned_data['email'],
            )
        except User.DoesNotExist:
            messages.error(request, _("This account does not exist."))
        finally:
            # Virtually fill the password reset form from Django Contrib Auth
            password_reset = PasswordResetForm(data={'email': user.email})
            if password_reset.is_valid():
                password_reset.save(
                    request=request,
                    use_https=request.is_secure(),
                )
                messages.success(request, _("A reset email was sent."))
                return redirect(reverse('index'))
            else:
                messages.error(request, _("The email is invalid."))

    return form({'userform': userform}, 'captivitate/user.html', request)
