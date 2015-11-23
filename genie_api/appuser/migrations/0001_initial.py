# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('key', models.CharField(max_length=256, serialize=False, primary_key=True)),
                ('user_agent', models.CharField(max_length=512, null=True)),
                ('time_zone', models.CharField(max_length=512, null=True)),
                ('created', models.DateTimeField(verbose_name=b'created', db_index=True)),
                ('used', models.DateTimeField(null=True, verbose_name=b'used', db_index=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'camoji_session',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(unique=True, serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.CharField(max_length=256, db_index=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('username', models.CharField(max_length=128, db_index=True)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.AddField(
            model_name='session',
            name='user',
            field=models.ForeignKey(related_name='+', to='appuser.User'),
        ),
    ]
