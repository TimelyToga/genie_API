# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appuser', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.IntegerField(unique=True, serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('content', models.TextField(blank=True)),
                ('reply_number', models.IntegerField(default=0)),
                ('created_by', models.ForeignKey(to='appuser.User')),
            ],
            options={
                'ordering': ('created',),
                'db_table': 'post',
            },
        ),
    ]
