# Generated by Django 2.1.4 on 2019-06-03 08:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='create_time',
            field=models.DateField(default=datetime.datetime(2019, 6, 3, 16, 12, 56, 289231)),
            preserve_default=False,
        ),
    ]
