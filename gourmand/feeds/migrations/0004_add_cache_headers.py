# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0003_add_gid_validator'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='etag',
            field=models.TextField(editable=False, default='', blank=True),
        ),
        migrations.AddField(
            model_name='feed',
            name='last_modified',
            field=models.TextField(editable=False, default='', blank=True),
        ),
    ]
