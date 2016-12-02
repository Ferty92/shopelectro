# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-21 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopelectro', '0008_create_custom_pages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='in_stock',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.RemoveField(
            model_name='category',
            name='slug',
        ),
    ]