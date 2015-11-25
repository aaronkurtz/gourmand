# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='personalarticle',
            unique_together=set([('sub', 'article')]),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together=set([('owner', 'feed')]),
        ),
    ]
