# Generated by Django 4.2 on 2023-04-25 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resources',
            name='exp',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='resources',
            name='gold',
            field=models.IntegerField(default=100),
        ),
        migrations.AlterField(
            model_name='resources',
            name='lvl',
            field=models.IntegerField(default=1),
        ),
    ]
