# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0006_remove_category_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='title',
            field=models.TextField(default='title'),
            preserve_default=False,
        ),
    ]
