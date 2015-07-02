# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0003_crawler'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crawler',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False),
        ),
        migrations.AlterField(
            model_name='crawler',
            name='template',
            field=models.ForeignKey(to='interface.Template', default=None),
        ),
    ]
