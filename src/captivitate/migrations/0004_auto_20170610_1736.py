# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import macaddress.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('captivitate', '0003_machines'),
    ]

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('mac_address', macaddress.fields.MACAddressField(max_length=17, unique=True, integer=False)),
                ('proprio', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.RemoveField(
            model_name='machines',
            name='proprio',
        ),
        migrations.DeleteModel(
            name='Machines',
        ),
    ]
