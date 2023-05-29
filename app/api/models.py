import sys
from django.db import models
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


ITEM_TYPES = [
    ('helmet', 'helmet'),
    ('armor', 'armor'),
    ('gloves', 'gloves'),
    ('boots', 'boots'),
    ('trousers', 'trousers'),
    ('weapon', 'weapon')
]


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

    def __str__(self):
        return str(self.user.name)

    @receiver(post_save, sender=get_user_model())
    def create_resource(sender, instance, created, **kwargs):
        if created:
            Resources.objects.create(user=instance)


class Character(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    armor = models.IntegerField(default=0)
    magicResist = models.IntegerField(default=0)
    health = models.IntegerField(default=100)
    damage = models.IntegerField(default=10)

    def __str__(self):
        return str(self.user.name)

    @receiver(post_save, sender=get_user_model())
    def create_character(sender, instance, created, **kwargs):
        if created:
            Character.objects.create(user=instance)


class Item(models.Model):
    name = models.CharField(max_length=100)
    itemType = models.CharField(max_length=100, null=True, choices=ITEM_TYPES)
    armor = models.IntegerField(default=0)
    magicResist = models.IntegerField(default=0)
    health = models.IntegerField(default=0)
    damage = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class UserItems(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, unique=True)
    item = models.ManyToManyField(Item, blank=True)

    def __str__(self):
        return str(self.user.name) + ' [' + str(self.item.count()) + ']'

    @receiver(post_save, sender=get_user_model())
    def create_characteritem(sender, instance, created, **kwargs):
        if created:
            UserItems.objects.create(user=instance)



class CharacterItem(models.Model):
    """Model for items already equiped by character"""
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    slot = models.CharField(max_length=100, choices=ITEM_TYPES, default='weapon')

    def __str__(self):
        return str(self.slot) + ' ' + str(self.character.user.name)

    def validate(self):
        # Check if there's already an equipped item of the same type
        equipped_items = CharacterItem.objects.filter(character=self.character).exclude(id=self.id)
        user_items = UserItems.objects.get(user=self.character.user)
        is_equipped = False
        for item in user_items.item.all():
            if item.id == self.item.id:
                is_equipped = True
        if not is_equipped:
            raise ValidationError({'item': 'This item is not in player inventory!'})
        for equipped_item in equipped_items:
            if equipped_item.slot == self.slot and equipped_item.item.item_type == self.item.item_type:

                raise ValidationError({'item': 'Cannot equip more than one item of the same type in this slot'})
        if self.slot != self.item.item_type:
            raise ValidationError({'item': 'Invalid slot for this item'})

    def clean(self):
        if self.item:
            self.validate()
        
    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
    
    @receiver(m2m_changed, sender=UserItems.item.through)
    def remove_related_character_item(sender, instance, action, pk_set, **kwargs):
        if action == 'post_remove':
            for pk in pk_set:
                character = Character.objects.get(user=instance.user)
                char_item = CharacterItem.objects.get(character=character, item=pk)
                char_item.item = None
                char_item.save()

    @receiver(post_save, sender=Character)
    def create_characteritem(sender, instance, created, **kwargs):
        if created:
            CharacterItem.objects.create(character=instance, slot='weapon')
            CharacterItem.objects.create(character=instance, slot='helmet')
            CharacterItem.objects.create(character=instance, slot='armor')
            CharacterItem.objects.create(character=instance, slot='gloves')
            CharacterItem.objects.create(character=instance, slot='boots')
            CharacterItem.objects.create(character=instance, slot='trousers')


class Enemy(models.Model):
    name = models.CharField(max_length=255)
    hp = models.IntegerField()
    armor = models.IntegerField()
    magicResist = models.IntegerField()
    damage = models.IntegerField()
    lvl = models.IntegerField()
    loot = models.ManyToManyField(Item)