# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0007_auto_20150708_0820'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crawler',
            name='active',
        ),
    ]
