# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def get_title(apps, schema_editor):
    Subscription = apps.get_model('subscriptions', 'Subscription')
    for row in Subscription.objects.all():
        row.title = row.feed.title
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0007_add_title_to_subs'),
    ]

    operations = [
        migrations.RunPython(get_title, reverse_code=migrations.RunPython.noop)
    ]
