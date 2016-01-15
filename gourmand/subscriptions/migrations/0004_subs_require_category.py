# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0003_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='category',
            field=models.ForeignKey(to='subscriptions.Category'),
        ),
    ]
