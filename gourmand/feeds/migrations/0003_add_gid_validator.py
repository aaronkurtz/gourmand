# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0002_articles_and_extras'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='gid',
            field=models.TextField(verbose_name='Global Identifier', validators=[django.core.validators.MinLengthValidator(1, message='GID can not be blank')]),
        ),
    ]
