# Generated by Django 4.2.1 on 2024-11-21 22:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_location_xcoordinate_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userlocation',
            name='isTraveling',
        ),
        migrations.AddField(
            model_name='userlocation',
            name='travel_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 21, 22, 27, 26, 914287, tzinfo=datetime.timezone.utc)),
        ),
    ]
