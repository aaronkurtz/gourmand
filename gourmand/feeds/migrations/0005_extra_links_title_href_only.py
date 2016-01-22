# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0004_add_cache_headers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extralink',
            name='rel',
        ),
        migrations.RemoveField(
            model_name='extralink',
            name='type',
        ),
        migrations.AddField(
            model_name='extralink',
            name='title',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]
