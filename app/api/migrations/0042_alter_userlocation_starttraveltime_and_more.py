# Generated by Django 4.2.1 on 2025-03-17 22:37

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_enemy_location_alter_questrequirement_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlocation',
            name='startTravelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 17, 22, 37, 37, 636973, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='travelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 17, 22, 37, 37, 636962, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='LocationElement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('npc', 'NPC'), ('enemy', 'Enemy'), ('object', 'Interactive Object')], max_length=10)),
                ('name', models.CharField(max_length=255)),
                ('position_x', models.IntegerField()),
                ('position_y', models.IntegerField()),
                ('dialog_id', models.IntegerField(blank=True, null=True)),
                ('enemy_id', models.IntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='elements', to='api.location')),
            ],
        ),
    ]
