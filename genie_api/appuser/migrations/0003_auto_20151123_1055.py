# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appuser', '0002_auto_20151123_1054'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='db_key',
            new_name='dbkey',
        ),
    ]
