from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("User must provide an email address")
        if not name:
            raise ValueError("User must provide a name")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, name, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have superuser set as True'))
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff set as True'))
        return self.create_user(email, name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=64, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()


class Resources(models.Model):
    """Resources model for user"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    gold = models.IntegerField(default=100)
    lvl = models.IntegerField(default=1)
    exp = models.IntegerField(default=0)

    @receiver(post_save, sender=get_user_model())
    def create_resource(sender, instance, created, **kwargs):
        if created:
            Resources.objects.create(user=instance)


class Character(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    armor = models.IntegerField(default=0)
    magic_resist = models.IntegerField(default=0)
    health = models.IntegerField(default=0)
    damage = models.IntegerField(default=0)

    @receiver(post_save, sender=get_user_model())
    def create_character(sender, instance, created, **kwargs):
        if created:
            Character.objects.create(user=instance)


class Item(models.Model):
    name = models.CharField(max_length=100)
    weapon_type = models.BooleanField(default=False) # True if weapon, False if armor
    armor = models.IntegerField(default=0)
    magic_resist = models.IntegerField(default=0)
    health = models.IntegerField(default=0)
    damage = models.IntegerField(default=0)


class CharacterItem(models.Model):
    """Model for items already equiped by character"""
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)

    def unequip_item(character: Character, item: Item):
        if item.weapon_type: # If it's a weapon
            character.weapon = None
            character.damage -= item.damage
        else: # If it's armor
            if item.armor_type == 'helmet':
                character.helmet = None
            elif item.armor_type == 'armor':
                character.armor = None
            elif item.armor_type == 'boots':
                character.boots = None
            elif item.armor_type == 'gloves':
                character.gloves = None
            elif item.armor_type == 'trousers':
                character.trousers = None
            character.armor -= item.armor
            character.magic_resist -= item.magic_resist
        character.health -= item.health
        character.save()

    def equip_item(self, character: Character, item: Item):
        if item.weapon_type: # If it's a weapon
            if character.weapon:
                self.unequip_item(character, character.weapon)
            character.weapon = item
            character.damage += item.damage
        else: # If it's armor
            if item.armor_type == 'helmet':
                if character.helmet:
                    self.unequip_item(character, character.helmet)
                character.helmet = item
            elif item.armor_type == 'armor':
                if character.armor:
                    self.unequip_item(character, character.armor)
                character.armor = item
            elif item.armor_type == 'boots':
                if character.boots:
                    self.unequip_item(character, character.boots)
                character.boots = item
            elif item.armor_type == 'gloves':
                if character.gloves:
                    self.unequip_item(character, character.gloves)
                character.gloves = item
            elif item.armor_type == 'trousers':
                if character.trousers:
                    self.unequip_item(character, character.trousers)
                character.trousers = item
            character.armor += item.armor
            character.magic_resist += item.magic_resist
        character.health += item.health
        character.save()

    @receiver(post_save, sender=Character)
    def create_characteritem(sender, instance, created, **kwargs):
        if created:
            CharacterItem.objects.create(character=instance)


class UserItems(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    item = models.ManyToManyField(Item, blank=True)

    @receiver(post_save, sender=get_user_model())
    def create_characteritem(sender, instance, created, **kwargs):
        if created:
            UserItems.objects.create(user=instance)


class Enemy(models.Model):
    name = models.CharField(max_length=255)
    hp = models.IntegerField()
    armor = models.IntegerField()
    magic_resists = models.IntegerField()
    damage = models.IntegerField()
    lvl = models.IntegerField()
    loot = models.ManyToManyField(Item)