# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0008_remove_crawler_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawler',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
