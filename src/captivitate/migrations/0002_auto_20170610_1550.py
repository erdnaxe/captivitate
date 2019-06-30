# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('captivitate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='comment',
            field=models.CharField(blank=True, help_text='Commentaire, promo', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='pseudo',
            field=models.CharField(unique=True, help_text='Doit contenir uniquement des lettres, chiffres, ou tirets. ', max_length=32),
        ),
    ]
