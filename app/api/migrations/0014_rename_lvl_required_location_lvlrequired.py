# Generated by Django 4.2.1 on 2023-05-30 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_location_store_remove_enemy_loot_storeitem_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='lvl_required',
            new_name='lvlRequired',
        ),
    ]