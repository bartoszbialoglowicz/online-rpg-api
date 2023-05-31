# Generated by Django 4.2 on 2023-05-02 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_characteritem_item_alter_useritems_item'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='weapon_type',
        ),
        migrations.AddField(
            model_name='item',
            name='armor_type',
            field=models.CharField(choices=[('helmet', 'helmet'), ('armor', 'armor'), ('gloves', 'gloves'), ('boots', 'gloves'), ('trousers', 'trousers'), ('weapon', 'weapon')], max_length=100, null=True),
        ),
    ]