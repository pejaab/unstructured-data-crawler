# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0003_crawler'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crawler',
            old_name='result',
            new_name='results',
        ),
    ]
