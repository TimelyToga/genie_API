# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appuser', '0003_auto_20151123_1055'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='dbkey',
            new_name='id',
        ),
    ]
