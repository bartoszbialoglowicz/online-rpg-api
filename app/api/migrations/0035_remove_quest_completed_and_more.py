# Generated by Django 4.2.1 on 2025-02-16 12:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_userquest_remove_questrequirement_completed_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quest',
            name='completed',
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='startTravelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 16, 12, 38, 58, 413765, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='travelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 16, 12, 38, 58, 413743, tzinfo=datetime.timezone.utc)),
        ),
    ]
