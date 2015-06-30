# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0004_auto_20150630_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawler',
            name='url',
            field=models.URLField(default='http://www.etoz.ch'),
            preserve_default=False,
        ),
    ]
