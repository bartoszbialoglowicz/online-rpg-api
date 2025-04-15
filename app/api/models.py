from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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

ITEM_RARITY = [
    ('common', 'common'),
    ('rare', 'rare'),
    ('mythic', 'mythic'),
    ('legendary', 'legendary')
]

QUEST_PROGRESS = [
    ('completed', 'completed'),
    ('in_progress', 'in_progress'),
    ('not_started', 'not_started')
]

QUEST_TYPE = [
    ('main', 'main'),
    ('side', 'side')
]

QUEST_TYPE_CHOICES = [
    ('kill', 'Kill'),
    ('collect', 'Collect'),
    ('explore', 'Explore'),
    ('talk', 'Talk'),
]


ELEMENT_TYPE_CHOICES = [
    ("npc", "NPC"),
    ("enemy", "Enemy"),
    ("object", "Interactive Object"),
    ("item", "Item"),
    ("location", "Location"),
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
    is_new = models.BooleanField(default=True)
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
    criticalHitChance = models.DecimalField(default=0.05, max_digits=5, decimal_places=2)
    criticalHitDamage = models.DecimalField(default=1.5, max_digits=5, decimal_places=2)
    health = models.IntegerField(default=100)
    damage = models.IntegerField(default=10)

    def __str__(self):
        return str(self.user.name)
    
    def get_item_stats(self):
        equipped_items = CharacterItem.objects.filter(character=self).select_related('item')
        item_stats = {
            'armor': sum(item.item.armor for item in equipped_items if item.item),
            'magicResist': sum(item.item.magicResist for item in equipped_items if item.item),
            'health': sum(item.item.health for item in equipped_items if item.item),
            'damage': sum(item.item.damage for item in equipped_items if item.item),
            'criticalHitChance': sum(item.item.criticalHitChance for item in equipped_items if item.item),
            'criticalHitDamage': sum(item.item.criticalHitDamage for item in equipped_items if item.item)
        }

        return item_stats
    
    def get_character_object_with_item_stats(self):
        item_stats = self.get_item_stats()
        return Character(
            armor=self.armor + item_stats['armor'],
            magicResist=self.magicResist + item_stats['magicResist'],
            health=self.health + item_stats['health'],
            damage=self.damage + item_stats['damage'],
            criticalHitChance=self.criticalHitChance + item_stats['criticalHitChance'],
            criticalHitDamage=self.criticalHitDamage + item_stats['criticalHitDamage'],
            user=self.user,
            pk=self.pk
        )

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
    criticalHitChance = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    criticalHitDamage = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    goldValue = models.IntegerField(default=0)
    imageUrl = models.ImageField(upload_to=upload_to, blank=True, null=True)
    rarity = models.CharField(max_length=32, choices=ITEM_RARITY)
    lvlRequired = models.IntegerField(default=1)

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
    
    def add_item(item_id, user_pk):
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            raise ValidationError({'item': "Provided item does not exists"})
        
        try:
            user = CustomUser.objects.get(pk=user_pk)
        except CustomUser.DoesNotExist:
            raise ValidationError({'user': 'Provided user does not exists'})
        
        new_item = UserItems.objects.create(user=user, item=item)
        new_item.save()

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
    xCoordinate = models.IntegerField(default=0)
    yCoordinate = models.IntegerField(default=0)

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
    

class SubLocation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    parent_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="sublocations")
    imageUrl = models.ImageField(upload_to="images/", blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} (w {self.parent_location.name})"


class LocationElement(models.Model):
    location = models.ForeignKey(
        Location, null=True, blank=True, on_delete=models.CASCADE, related_name="elements"
    )
    sublocation = models.ForeignKey(
        SubLocation, null=True, blank=True, on_delete=models.CASCADE, related_name="elements"
    )
    
    type = models.CharField(max_length=10, choices=ELEMENT_TYPE_CHOICES)
    npc = models.ForeignKey("NPC", null=True, blank=True, on_delete=models.SET_NULL)
    enemy = models.ForeignKey("Enemy", null=True, blank=True, on_delete=models.SET_NULL)
    item = models.ForeignKey("Item", null=True, blank=True, on_delete=models.SET_NULL)
    location_element = models.ForeignKey("Location", null=True, blank=True, on_delete=models.SET_NULL)
    sublocation_element = models.ForeignKey("SubLocation", null=True, blank=True, on_delete=models.SET_NULL)

    position_x = models.IntegerField()
    position_y = models.IntegerField()
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.location and self.sublocation:
            raise ValueError("An item can only be assigned to one location (Location or SubLocation).")
        if not self.location and not self.sublocation:
            raise ValueError("An item must be assigned to Location or Sublocation")
        super().save(*args, **kwargs)

    def __str__(self):
        prefix = self.location.name if self.location else self.sublocation.name
        if self.npc:
            return f"{prefix} -> {self.npc.name}"
        elif self.enemy:
            return f"{prefix} ->{self.enemy.name}"
        elif self.location_element:
            return f"{prefix} -> {self.location_element.name}"
        elif self.sublocation_element:
            return f"{prefix} -> {self.sublocation_element.name}"
        return f"{self.type} ({self.id})"

class Enemy(models.Model):
    name = models.CharField(max_length=255)
    health = models.IntegerField()
    armor = models.IntegerField()
    magicResist = models.IntegerField()
    damage = models.IntegerField()
    criticalHitChance = models.DecimalField(default=0.05, max_digits=5, decimal_places=2)
    criticalHitDamage = models.DecimalField(default=1.5, max_digits=5, decimal_places=2)
    lvl = models.IntegerField()
    exp = models.IntegerField(default=10)
    imgSrc = models.ImageField(blank=True, null=True, upload_to=upload_to)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=Location.get_or_create_default_location().pk)

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
    

class NPC(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    imageUrl = models.ImageField()

    def __str__(self):
        return (f'{self.name} [{self.location.name}]')


class Store(models.Model):
    STORE_TYPES = [
        ('weapon', 'weapon'),
        ('alchemist', 'alchemist')
    ]
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=64, choices=STORE_TYPES)
    npc = models.ForeignKey(NPC, on_delete=models.CASCADE)

    def clean(self):
        if not self.npc.location.pk == self.location.pk:
            raise ValidationError({'location': 'Provided location has to be the same as npc location.'})
        
    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


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


class Dialog(models.Model):
    npc = models.ForeignKey(NPC, on_delete=models.CASCADE, related_name="dialogs")
    content = models.TextField()
    event_id = models.CharField(max_length=100, blank=True, null=True)
    starter = models.BooleanField(default=False)

    def __str__(self):
        return f"Dialog by {self.npc.name}: {self.content[:50]}"


class DialogOption(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name="options")
    content = models.CharField(max_length=255)
    next_dialog = models.ForeignKey(Dialog, on_delete=models.SET_NULL, blank=True, null=True, related_name="previous_options")
    effects = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Option for Dialog {self.dialog.id}: {self.content[:50]}"


class StoryState(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="story_states")
    key = models.CharField(max_length=100)
    value = models.JSONField()

    class Meta:
        unique_together = ('user', 'key')

    def __str__(self):
        return f"State for {self.user.username}: {self.key} = {self.value}"

    @receiver(post_save, sender=get_user_model())
    def create_story_state(sender, instance, created, **kwargs):
        if created:
            StoryState.objects.create(user=instance, key="initial_story", value={})


class Quest(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=QUEST_TYPE, default='main')
    description = models.TextField()
    gold_reward = models.IntegerField(null=True, blank=True)
    item_reward = models.ForeignKey('Item', null=True, blank=True, on_delete=models.SET_NULL)
    exp_reward = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class QuestRequirement(models.Model):
    quest = models.ForeignKey(Quest, related_name='requirements', on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=QUEST_TYPE_CHOICES)
    amount = models.IntegerField(null=True, blank=True)
    # Refers to the target object type
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # Refers to the target object id
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_content_type', 'target_object_id')
    # Defines the position of the requirement in the quest
    position = models.PositiveIntegerField(default=1)
    # Defines which path it belongs to
    path = models.PositiveIntegerField(default=1)
    # Defines if the requirement ends the quersts
    is_last = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type} - {self.quest.title}"
    

class UserQuest(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    progress = models.CharField(max_length=20, choices=QUEST_PROGRESS, default='not_started')

    @receiver(post_save, sender=get_user_model())
    def create_user_quest(sender, instance, created, **kwargs):
        if created:
            for quest in Quest.objects.all():
                UserQuest.objects.create(user=instance, quest=Quest.objects.get(pk=1))

    def __str__(self):
        return f"{self.user.name} - {self.quest.title}"


class UserQuestRequirement(models.Model):
    user_quest = models.ForeignKey(UserQuest, related_name='requirements', on_delete=models.CASCADE)
    requirement = models.ForeignKey(QuestRequirement, on_delete=models.CASCADE)
    progress = models.CharField(max_length=20, choices=QUEST_PROGRESS, default='not_started')
    amount_progress = models.IntegerField(default=0)

    # Create user quest requirements for specific quest whenever user starts a quest
    @receiver(post_save, sender=UserQuest)
    def create_user_quest_requirements(sender, instance, created, **kwargs):
        if created:
            for requirement in instance.quest.requirements.all():
                progress = 'in_progress' if requirement.position == 1 else 'not_started'
                UserQuestRequirement.objects.create(user_quest=instance, requirement=requirement, progress=progress)

    def __str__(self):
        return f"{self.user_quest.user.name} - {self.requirement.quest.title} ({self.requirement.type})"
    