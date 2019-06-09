# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

import ipaddress

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.template import Context, loader
from django.template.context_processors import csrf
from django.utils import timezone
from reversion import revisions as reversion

from portail_captif.settings import REQ_EXPIRE_STR, EMAIL_FROM, ASSO_NAME, \
    ASSO_EMAIL, SITE_NAME, CAPTIVE_IP_RANGE, CAPTIVE_WIFI
from users.forms import PassForm, ResetPasswordForm
from users.models import InfoForm, BaseInfoForm, Machine, mac_from_ip
from users.models import User, Request


def form(ctx, template, request):
    ctx.update(csrf(request))
    return render(request, template, ctx)


def index(request):
    """
    Show logged in user profile or index page
    """
    if request.user.is_authenticated():
        try:
            users = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
            raise Http404
        machines_list = Machine.objects.filter(proprio=users)
        return render(
            request,
            'users/profile.html',
            {
                'user': users,
                'machines_list': machines_list,
            }
        )
    else:
        return form({}, 'users/index.html', request)


def password_change_action(u_form, user, request, req=False):
    """ Fonction qui effectue le changeemnt de mdp bdd"""
    if u_form.cleaned_data['passwd1'] != u_form.cleaned_data['passwd2']:
        messages.error(request, "Les 2 mots de passe différent")
        return form({'userform': u_form}, 'users/user.html', request)
    user.set_password(u_form.cleaned_data['passwd1'])
    with transaction.atomic(), reversion.create_revision():
        user.save()
        reversion.set_comment("Réinitialisation du mot de passe")
    messages.success(request, "Le mot de passe a changé")
    if req:
        req.delete()
        return redirect("/")
    return redirect("/")


def reset_passwd_mail(req, request):
    """ Prend en argument un request, envoie un mail de réinitialisation de mot de pass """
    t = loader.get_template('users/email_passwd_request')
    c = Context({
        'name': str(req.user.name) + ' ' + str(req.user.surname),
        'asso': ASSO_NAME,
        'asso_mail': ASSO_EMAIL,
        'site_name': SITE_NAME,
        'url': request.build_absolute_uri(
            reverse('users:process', kwargs={'token': req.token})),
        'expire_in': REQ_EXPIRE_STR,
    })
    send_mail('Votre compte %s' % SITE_NAME, t.render(c),
              EMAIL_FROM, [req.user.email], fail_silently=False)
    return


def new_user(request):
    """ Vue de création d'un nouvel utilisateur, envoie un mail pour le mot de passe"""
    user = BaseInfoForm(request.POST or None)
    if user.is_valid():
        user = user.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            user.save()
            reversion.set_comment("Création")
        req = Request()
        req.type = Request.PASSWD
        req.user = user
        req.save()
        reset_passwd_mail(req, request)
        messages.success(request,
                         "L'utilisateur %s a été créé, un mail pour l'initialisation du mot de passe a été envoyé" % user.pseudo)
        capture_mac(request, user)
        return redirect("/")
    return form({'userform': user}, 'users/user.html', request)


@login_required
def edit_info(request, userid):
    """ Edite un utilisateur à partir de son id, si l'id est différent de request.user, vérifie la possession du droit admin """
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/")
    if not request.user.is_admin and user != request.user:
        messages.error(request,
                       "Vous ne pouvez pas modifier un autre user que vous sans droit admin")
        return redirect("/")
    if not request.user.is_admin:
        user = BaseInfoForm(request.POST or None, instance=user)
    else:
        user = InfoForm(request.POST or None, instance=user)
    if user.is_valid():
        with transaction.atomic(), reversion.create_revision():
            user.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in user.changed_data))
        messages.success(request, "L'user a bien été modifié")
        return redirect("/")
    return form({'userform': user}, 'users/user.html', request)


@login_required
def password(request, userid):
    """ Reinitialisation d'un mot de passe à partir de l'userid,
    pour self par défaut, pour tous sans droit si droit admin,
    pour tous si droit bureau """
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/")
    if not request.user.is_admin and user != request.user:
        messages.error(request,
                       "Vous ne pouvez pas modifier un autre user que vous sans droit admin")
        return redirect("/" + str(request.user.id))
    u_form = PassForm(request.POST or None)
    if u_form.is_valid():
        return password_change_action(u_form, user, request)
    return form({'userform': u_form}, 'users/user.html', request)


def get_ip(request):
    """Returns the IP of the request, accounting for the possibility of being
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
    if ipaddress.ip_address(remote_ip) in ipaddress.ip_network(
            CAPTIVE_IP_RANGE):
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
                           "Merci de vous connecter sur le réseau du portail captif pour capturer la machine (WiFi %s)" % CAPTIVE_WIFI)


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
    userform = ResetPasswordForm(request.POST or None)
    if userform.is_valid():
        try:
            user = User.objects.get(pseudo=userform.cleaned_data['pseudo'],
                                    email=userform.cleaned_data['email'])
        except User.DoesNotExist:
            messages.error(request, "Cet utilisateur n'existe pas")
            return form({'userform': userform}, 'users/user.html', request)
        req = Request()
        req.type = Request.PASSWD
        req.user = user
        req.save()
        reset_passwd_mail(req, request)
        messages.success(request,
                         "Un mail pour l'initialisation du mot de passe a été envoyé")
        redirect("/")
    return form({'userform': userform}, 'users/user.html', request)


def process(request, token):
    valid_reqs = Request.objects.filter(expires_at__gt=timezone.now())
    req = get_object_or_404(valid_reqs, token=token)

    if req.type == Request.PASSWD:
        return process_passwd(request, req)
    else:
        messages.error(request, "Entrée incorrecte, contactez un admin")
        redirect("/")


def process_passwd(request, req):
    u_form = PassForm(request.POST or None)
    user = req.user
    if u_form.is_valid():
        return password_change_action(u_form, user, request, req=req)
    return form({'userform': u_form}, 'users/user.html', request)
