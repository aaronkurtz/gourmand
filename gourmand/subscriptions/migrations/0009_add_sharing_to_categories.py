# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0008_get_title_from_feed'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='shared',
            field=models.BooleanField(default=False),
        ),
    ]
