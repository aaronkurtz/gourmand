# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0009_add_sharing_to_categories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='public',
        ),
    ]
