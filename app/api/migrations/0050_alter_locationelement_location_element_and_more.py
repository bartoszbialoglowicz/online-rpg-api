# Generated by Django 4.2.1 on 2025-03-23 12:28

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_alter_locationelement_location_element_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationelement',
            name='location_element',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.location'),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='startTravelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 23, 12, 28, 46, 398981, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='travelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 23, 12, 28, 46, 398969, tzinfo=datetime.timezone.utc)),
        ),
    ]
