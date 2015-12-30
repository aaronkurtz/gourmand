# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscriptions', '0002_make_unique_per_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('order', models.PositiveSmallIntegerField()),
                ('name', models.TextField()),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('order',),
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.AddField(
            model_name='subscription',
            name='category',
            field=models.ForeignKey(null=True, blank=True, to='subscriptions.Category', default=None),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('owner', 'order'), ('owner', 'name')]),
        ),
    ]
