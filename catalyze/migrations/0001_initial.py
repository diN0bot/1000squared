# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-29 09:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CatalystPic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pic', models.ImageField(upload_to=b'uploaded_pics/')),
            ],
        ),
    ]
