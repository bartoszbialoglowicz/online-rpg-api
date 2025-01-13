# Generated by Django 4.2.1 on 2024-11-30 19:34

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_alter_userlocation_starttraveltime_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlocation',
            name='startTravelTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 30, 19, 33, 44, 352134, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='travelTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 30, 19, 33, 44, 352123, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='NPC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('imageUrl', models.ImageField(upload_to='')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.location')),
            ],
        ),
        migrations.AddField(
            model_name='store',
            name='npc',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.npc'),
            preserve_default=False,
        ),
    ]
