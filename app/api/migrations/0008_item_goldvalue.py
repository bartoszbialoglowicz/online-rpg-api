# Generated by Django 4.2.1 on 2023-10-02 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_item_imageurl_alter_enemyloot_rarity'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='goldValue',
            field=models.IntegerField(default=0),
        ),
    ]