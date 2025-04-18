# Generated by Django 4.2.1 on 2025-03-09 18:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_alter_userlocation_starttraveltime_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userquest',
            name='completed',
        ),
        migrations.RemoveField(
            model_name='userquestrequirement',
            name='completed',
        ),
        migrations.AddField(
            model_name='userquest',
            name='progress',
            field=models.CharField(choices=[('completed', 'completed'), ('in_progress', 'in_progress'), ('not_started', 'not_started')], default='not_started', max_length=20),
        ),
        migrations.AddField(
            model_name='userquestrequirement',
            name='progress',
            field=models.CharField(choices=[('completed', 'completed'), ('in_progress', 'in_progress'), ('not_started', 'not_started')], default='not_started', max_length=20),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='startTravelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 9, 18, 25, 27, 730089, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='travelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 9, 18, 25, 27, 730078, tzinfo=datetime.timezone.utc)),
        ),
    ]
