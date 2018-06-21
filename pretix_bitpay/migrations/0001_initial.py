# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-20 15:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pretixbase', '0095_auto_20180604_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferencedBitPayObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(db_index=True, max_length=190, unique=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pretixbase.Order')),
            ],
        ),
    ]