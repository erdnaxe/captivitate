# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-06-30 20:08
from __future__ import unicode_literals

import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


def migrate_user(apps, schema_editor):
    """
    Migrate old custom user to Django Contrib Auth user
    """
    User = apps.get_model('captivitate', 'User')
    for user in User.objects.all():
        user.is_staff = user.is_superuser
        user.is_active = (user.state == 0)
        user.date_joined = user.registered
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('captivitate', '0009_use_django_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
        ),
        migrations.RunPython(migrate_user),
    ]
