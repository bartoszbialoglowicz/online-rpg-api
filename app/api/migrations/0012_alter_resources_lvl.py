# Generated by Django 4.2.1 on 2023-10-09 20:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_userlvl_enemy_exp_alter_resources_lvl_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resources',
            name='lvl',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.userlvl'),
        ),
    ]