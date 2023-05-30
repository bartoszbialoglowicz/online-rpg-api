# Generated by Django 4.2 on 2023-05-30 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_userlocation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='region',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='api.region'),
        ),
    ]
