# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0005_extra_links_title_href_only'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='extracontent',
            unique_together=set([('article', 'content')]),
        ),
        migrations.AlterUniqueTogether(
            name='extralink',
            unique_together=set([('article', 'link')]),
        ),
    ]
