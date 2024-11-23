from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta


ITEM_TYPES = [
    ('helmet', 'helmet'),
    ('armor', 'armor'),
    ('gloves', 'gloves'),
    ('boots', 'boots'),
    ('trousers', 'trousers'),
    ('weapon', 'weapon')
]

def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


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


class UserLvl(models.Model):
    lvl = models.IntegerField(unique=True)
    expPoints = models.IntegerField()

    def create_default_lvl():
        try:
            lvl = UserLvl.objects.get(lvl=1)
        except UserLvl.DoesNotExist:
            lvl = UserLvl.objects.create(lvl=1, expPoints=100)
        return lvl


class Resources(models.Model):
    """Resources model for user"""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    gold = models.IntegerField(default=100)
    lvl = models.ForeignKey(UserLvl, on_delete=models.CASCADE, default=1)
    exp = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user.name)
    
    def add_exp(self, exp_points):
        current_lvl = self.lvl.lvl
        current_exp = self.exp + exp_points
        
        while current_exp >= UserLvl.objects.get(lvl=current_lvl).expPoints:
            current_exp = current_exp - UserLvl.objects.get(lvl=current_lvl).expPoints
            current_lvl = current_lvl+1

        self.lvl = UserLvl.objects.get(lvl=current_lvl)
        self.exp = current_exp

        self.save()


    @receiver(post_save, sender=get_user_model())
    def create_resource(sender, instance, created, **kwargs):
        if created:
            Resources.objects.create(user=instance, lvl=UserLvl.create_default_lvl())


class Character(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    armor = models.IntegerField(default=0)
    magicResist = models.IntegerField(default=0)
    health = models.IntegerField(default=100)
    damage = models.IntegerField(default=10)

    def __str__(self):
        return str(self.user.name)
    
    # Remove current item stats from Character model
    def remove_equipped_item_stats(self, item_slot):
        try:
            character_item = CharacterItem.objects.get(character=self, slot=item_slot)
            if character_item.item is not None:
                self.armor -= character_item.item.armor
                self.magicResist -= character_item.item.magicResist
                self.health -= character_item.item.health
                self.damage -= character_item.item.damage

            self.save()

        except CharacterItem.DoesNotExist:
            pass

    # Replace current item stats with other item stats
    def replace_equipped_item_stats(self, item, slot):
        try:
            self.remove_equipped_item_stats(slot)
            new_item = item
            self.armor += new_item.armor
            self.magicResist += new_item.magicResist
            self.health += new_item.health
            self.damage += new_item.damage

            self.save()

        except CharacterItem.DoesNotExist or Item.DoesNotExist:
            pass

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
    goldValue = models.IntegerField(default=0)
    imageUrl = models.ImageField(upload_to=upload_to, blank=True, null=True)

    def __str__(self):
        return self.name
    

class CollectableItem(models.Model):
    name = models.CharField(max_length=100)
    goldValue = models.IntegerField()


class Potion(models.Model):
    name = models.CharField(max_length=100)
    hpValue = models.IntegerField()
    goldValue = models.IntegerField()

    
class UserItems(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def delete(self):
        eqItem = CharacterItem.objects.get(slot=self.item.itemType, character=self.user.character)
        if eqItem.item is not None:
            if eqItem.item.id == self.item.id:
                Character.objects.get(user=self.user).remove_equipped_item_stats(self.item.itemType)
                item = CharacterItem.objects.get(character=self.user.character, slot=self.item.itemType)
                item.item = None
                item.save()
        return super().delete()

    def __str__(self):
        return (f'[{self.user.name}] {self.item.name }')



class UserCollectableItem(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    collectableItem = models.ForeignKey(CollectableItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class UserPotions(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    potion = models.ForeignKey(Potion, on_delete=models.CASCADE)
    quantity = models.IntegerField()


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
        user_items = UserItems.objects.filter(user=self.character.user)
        is_equipped = False
        for useritem in user_items:
            if useritem.item.id == self.item.id:
                is_equipped = True
        if not is_equipped:
            raise ValidationError({'item': 'This item is not in player inventory!'})
        for equipped_item in equipped_items:
                if equipped_item.slot == self.slot and equipped_item.item.itemType == self.item.itemType:

                    raise ValidationError({'item': 'Cannot equip more than one item of the same type in this slot'})
        if self.slot != self.item.itemType:
            raise ValidationError({'item': 'Invalid slot for this item'})

    def clean(self):
        if self.item:
            self.validate()
        
    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

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
    health = models.IntegerField()
    armor = models.IntegerField()
    magicResist = models.IntegerField()
    damage = models.IntegerField()
    lvl = models.IntegerField()
    exp = models.IntegerField(default=10)
    imgSrc = models.ImageField(blank=True, null=True, upload_to=upload_to)

    

    def __str__(self):
        return self.name


class EnemyLoot(models.Model):
    enemy = models.ForeignKey(Enemy, on_delete=models.CASCADE)
    rarity = models.FloatField(
        validators=[
            MinValueValidator(0.0001),
            MaxValueValidator(1.0000)
        ]
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.enemy.name + ' [' +  self.item.name + ']'

class Region(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    
    def create_default_region():
        try:
            region = Region.objects.get(name="Default")
        except:
            region = Region.objects.create(name="Default", description="Default")
        return region
    

class Location(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, default=1)
    lvlRequired = models.IntegerField()
    description = models.TextField()
    imageUrl = models.ImageField(upload_to=upload_to, blank=True, null=True)
    xCoordinate = models.IntegerField()
    yCoordinate = models.IntegerField()

    def __str__(self):
        return (f'[{self.region}] {self.name}')
    
    def get_or_create_default_location():
        try:
            location = Location.objects.get(name="Przełęcz Mroźnego Wiatru")
        except:
            location = Location.objects.create(name="Default", region=Region.create_default_region(), lvlRequired=1, description="test")
        return location
    
    def get_neighboring_locations(location):
        return Location.objects.exclude(pk=location.pk).filter(
            (models.Q(xCoordinate=location.xCoordinate - 1) & models.Q(yCoordinate=location.yCoordinate)) |
            (models.Q(xCoordinate=location.xCoordinate + 1) & models.Q(yCoordinate=location.yCoordinate)) |
            (models.Q(xCoordinate=location.xCoordinate) & models.Q(yCoordinate=location.yCoordinate - 1)) |
            (models.Q(xCoordinate=location.xCoordinate) & models.Q(yCoordinate=location.yCoordinate + 1))
        )
    
    def get_location_by_coordinates(x, y):
        return Location.objects.get(xCoordinate=x, yCoordinate=y)
    

class Store(models.Model):
    STORE_TYPES = [
        ('weapon', 'weapon'),
        ('alchemist', 'alchemist')
    ]
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=64, choices=STORE_TYPES)

    def __str__(self):
        return (f'{self.location} - {self.name}')


class StoreItem(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.IntegerField()

    def __str__(self):
        return (f'[{self.store}] {self.item} ({self.price})')
    

class StorePotion(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    potion = models.ForeignKey(Potion, on_delete=models.CASCADE)
    price = models.IntegerField()


class StoreCollectableItem(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    collectableItem = models.ForeignKey(CollectableItem, on_delete=models.CASCADE)
    price = models.IntegerField()


class LocationEnemy(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    enemy = models.ForeignKey(Enemy, on_delete=models.CASCADE)

class UserLocation(models.Model):
    location = models.ForeignKey(Location, on_delete=models.SET_DEFAULT, default=1)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    travelTime = models.DateTimeField(default=timezone.now())
    startTravelTime = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return (f'{self.user} - {self.location}')


    @receiver(post_save, sender=get_user_model())
    def create_user_location(sender, instance, created, **kwargs):
        if created:
            UserLocation.objects.create(user=instance, location=Location.get_or_create_default_location())

    def can_move(self):
        return timezone.now() >= self.travelTime

    def update_travel_time(self, seconds):
        self.travelTime = timezone.now() + timedelta(seconds=seconds)
        self.startTravelTime = timezone.now()
        self.save()
        return self.travelTime, self.startTravelTime
    
    def update_user_location(self, location_id):
        try:
            target_location = Location.objects.get(pk=location_id)
        except Location.DoesNotExist:
            raise ValidationError({'location': "User can not travel to location that does not exist!"})
        
        self.location = target_location
        self.save()
        return self.location
            

class Fight(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    enemy = models.ForeignKey(Enemy, on_delete=models.CASCADE)
    currentPlayerHP = models.IntegerField()
    currentEnemyHP = models.IntegerField()
    isActive = models.BooleanField(default=False)


class Transaction(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    totalAmount = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    