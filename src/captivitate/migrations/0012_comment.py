# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-06-30 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('captivitate', '0011_cleanup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='comment',
            field=models.CharField(blank=True, max_length=255, verbose_name='comment'),
        ),
    ]
