# Generated by Django 4.2.1 on 2025-04-28 22:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_userlocation_starttraveltime_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlocation',
            name='startTravelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 28, 22, 57, 22, 502353, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='travelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 28, 22, 57, 22, 502333, tzinfo=datetime.timezone.utc)),
        ),
    ]
