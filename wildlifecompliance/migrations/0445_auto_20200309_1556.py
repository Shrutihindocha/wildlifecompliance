# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-03-09 07:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0444_auto_20200308_2138'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='licencespecies',
            options={'ordering': ['specie_id'], 'verbose_name': 'Licence species', 'verbose_name_plural': 'Licence species'},
        ),
    ]
