# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('href', models.URLField(verbose_name='HREF', unique=True, max_length=2048)),
                ('link', models.URLField(blank=True, max_length=2048)),
                ('title', models.TextField()),
            ],
        ),
    ]
