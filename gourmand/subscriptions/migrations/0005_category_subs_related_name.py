# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_subs_require_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='category',
            field=models.ForeignKey(related_name='subs', to='subscriptions.Category'),
        ),
    ]
