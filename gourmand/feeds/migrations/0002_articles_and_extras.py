# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when', models.DateTimeField()),
                ('title', models.TextField()),
                ('gid', models.TextField(verbose_name='Global Identifier')),
                ('main_content', models.TextField()),
                ('main_link', models.URLField(max_length=2048)),
                ('feed', models.ForeignKey(to='feeds.Feed')),
            ],
        ),
        migrations.CreateModel(
            name='ExtraContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('article', models.ForeignKey(to='feeds.Article')),
            ],
        ),
        migrations.CreateModel(
            name='ExtraLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rel', models.TextField()),
                ('type', models.TextField()),
                ('link', models.URLField(max_length=2048)),
                ('article', models.ForeignKey(to='feeds.Article')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('feed', 'gid')]),
        ),
    ]
