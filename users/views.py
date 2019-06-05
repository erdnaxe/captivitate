# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

import ipaddress

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.template import Context, loader
from django.template.context_processors import csrf
from django.utils import timezone
from reversion import revisions as reversion
from reversion.models import Version

from portail_captif.settings import REQ_EXPIRE_STR, EMAIL_FROM, ASSO_NAME, \
    ASSO_EMAIL, SITE_NAME, CAPTIVE_IP_RANGE, CAPTIVE_WIFI, PAGINATION_NUMBER
from users.forms import PassForm, ResetPasswordForm
from users.models import InfoForm, BaseInfoForm, Machine, StateForm, mac_from_ip
from users.models import User, Request


def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render(request, template, c)


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
    return redirect("/users/profil/" + str(user.id))


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
                         "L'utilisateur %s a été crée, un mail pour l'initialisation du mot de passe a été envoyé" % user.pseudo)
        capture_mac(request, user)
        return redirect("/users/profil/" + str(user.id))
    return form({'userform': user}, 'users/user.html', request)


@login_required
def edit_info(request, userid):
    """ Edite un utilisateur à partir de son id, si l'id est différent de request.user, vérifie la possession du droit admin """
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    if not request.user.is_admin and user != request.user:
        messages.error(request,
                       "Vous ne pouvez pas modifier un autre user que vous sans droit admin")
        return redirect("/users/profil/" + str(request.user.id))
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
        return redirect("/users/profil/" + userid)
    return form({'userform': user}, 'users/user.html', request)


@login_required
@permission_required('admin')
def state(request, userid):
    """ Changer l'etat actif/desactivé/archivé d'un user, need droit bureau """
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    state = StateForm(request.POST or None, instance=user)
    if state.is_valid():
        with transaction.atomic(), reversion.create_revision():
            state.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for field in state.changed_data))
        messages.success(request, "Etat changé avec succès")
        return redirect("/users/profil/" + userid)
    return form({'userform': state}, 'users/user.html', request)


@login_required
def password(request, userid):
    """ Reinitialisation d'un mot de passe à partir de l'userid,
    pour self par défaut, pour tous sans droit si droit admin,
    pour tous si droit bureau """
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    if not request.user.is_admin and user != request.user:
        messages.error(request,
                       "Vous ne pouvez pas modifier un autre user que vous sans droit admin")
        return redirect("/users/profil/" + str(request.user.id))
    u_form = PassForm(request.POST or None)
    if u_form.is_valid():
        return password_change_action(u_form, user, request)
    return form({'userform': u_form}, 'users/user.html', request)


@login_required
@permission_required('admin')
def index(request):
    """ Affiche l'ensemble des users, need droit admin """
    users_list = User.objects.order_by('registered').reverse()
    paginator = Paginator(users_list, PAGINATION_NUMBER)
    page = request.GET.get('page')
    try:
        users_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users_list = paginator.page(paginator.num_pages)
    return render(request, 'users/index.html', {'users_list': users_list})


@login_required
def history(request, object, id):
    """ Affichage de l'historique : (acl, argument)
    user : self, userid"""
    if object == 'user':
        try:
            object_instance = User.objects.get(pk=id)
        except User.DoesNotExist:
            messages.error(request, "Utilisateur inexistant")
            return redirect("/users/")
        if not request.user.is_admin and object_instance != request.user:
            messages.error(request,
                           "Vous ne pouvez pas afficher l'historique d'un autre user que vous sans droit admin")
            return redirect("/users/profil/" + str(request.user.id))
    elif object == 'machines':
        try:
            object_instance = Machine.objects.get(pk=id)
        except User.DoesNotExist:
            messages.error(request, "Machine inexistante")
            return redirect("/users/")
        if not request.user.is_admin and object_instance.proprio != request.user:
            messages.error(request,
                           "Vous ne pouvez pas afficher l'historique d'un autre user que vous sans droit admin")
            return redirect("/users/profil/" + str(request.user.id))
    else:
        messages.error(request, "Objet  inconnu")
        return redirect("/users/")
    reversions = Version.objects.get_for_object(object_instance)
    paginator = Paginator(reversions, PAGINATION_NUMBER)
    page = request.GET.get('page')
    try:
        reversions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reversions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reversions = paginator.page(paginator.num_pages)
    return render(request, 'portail_captif/history.html',
                  {'reversions': reversions, 'object': object_instance})


@login_required
def mon_profil(request):
    return redirect("/users/profil/" + str(request.user.id))


@login_required
def profil(request, userid):
    try:
        users = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    machines_list = Machine.objects.filter(proprio=users)
    if not request.user.is_admin and users != request.user:
        messages.error(request,
                       "Vous ne pouvez pas afficher un autre user que vous sans droit admin")
        return redirect("/users/profil/" + str(request.user.id))
    return render(
        request,
        'users/profil.html',
        {
            'user': users,
            'machines_list': machines_list,
        }
    )


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
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    capture_mac(request, users)
    return redirect("/users/profil/" + str(users.id))


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
    elif req.type == Request.EMAIL:
        return process_email(request, req=req)
    else:
        messages.error(request, "Entrée incorrecte, contactez un admin")
        redirect("/")


def process_passwd(request, req):
    u_form = PassForm(request.POST or None)
    user = req.user
    if u_form.is_valid():
        return password_change_action(u_form, user, request, req=req)
    return form({'userform': u_form}, 'users/user.html', request)
