# Generated by Django 4.2.1 on 2024-12-10 22:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_character_criticalhitchance_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_new',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='startTravelTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 10, 22, 24, 3, 581542, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='travelTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 10, 22, 24, 3, 581529, tzinfo=datetime.timezone.utc)),
        ),
    ]
