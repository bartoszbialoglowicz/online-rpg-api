# Generated by Django 4.2.1 on 2025-02-16 12:28

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_dialog_quest_alter_userlocation_starttraveltime_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserQuest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('quest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.quest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='questrequirement',
            name='completed',
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='startTravelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 16, 12, 28, 13, 482651, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='travelTime',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 16, 12, 28, 13, 482640, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='UserQuestRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('requirement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.questrequirement')),
                ('user_quest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_requirements', to='api.userquest')),
            ],
        ),
    ]
