from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError

from api import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'name', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8
            },
            'email': {
                'validators': [
                    UniqueValidator(
                        queryset=get_user_model().objects.all(),
                        message="Istnieje już konto o podanym adresie e-mail."
                    ),
                ]
            },
            'name': {
                'validators': [
                    UniqueValidator(
                        queryset=get_user_model().objects.all(),
                        message="Istnieje już konto z podaną nazwą uzytkownika."
                    ),
                ]
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):

    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')
        
        attrs['user'] = user
        return attrs


class UserLvlSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserLvl
        fields = ('lvl', 'expPoints')


class ResourcesSerializer(serializers.ModelSerializer):
    lvl = UserLvlSerializer(many=False)
    class Meta:
        model = models.Resources
        fields = '__all__'


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Character
        fields = ('armor', 'magicResist', 'health', 'damage')


class ItemSerializer(serializers.ModelSerializer):
    imageUrl = serializers.ImageField(required=False)
    class Meta:
        model = models.Item
        fields = '__all__'


class CollectableItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CollectableItem
        fields = '__all__'


class PotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Potion
        fields = '__all__'


class CharacterItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False, read_only=True)
    class Meta:
        model = models.CharacterItem
        fields = ('slot', 'item')


class UserItemsSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False, read_only=True)
    class Meta:
        model = models.UserItems
        fields = '__all__'
    
    def get_imageUrl(self, obj):
        # Get the request object from the context
        request = self.context.get('request')
        if obj.item.imageUrl:
            return request.build_absolute_uri(obj.item.imageUrl.url)
        return None


class UserCollectableItemsSerializer(serializers.ModelSerializer):
    collectableItem = CollectableItemSerializer(many=False, read_only=True)
    class Meta:
        model = models.UserCollectableItem
        fields = '__all__'
        

class UserPotionsSerializer(serializers.ModelSerializer):
    potion = PotionSerializer(many=False, read_only=True)
    class Meta:
        model = models.UserPotions
        fields = '__all__'


class EnemySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Enemy
        fields = '__all__'


class EnemyLootSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True, many=False)
    class Meta:
        model = models.EnemyLoot
        fields = ('item',)


class NPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NPC
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    npc = NPCSerializer(many=False, read_only=True)
    class Meta:
        model = models.Store
        fields = '__all__'


class StoreItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False, read_only=True)
    class Meta:
        model = models.StoreItem
        fields = '__all__'
    
    def get_imageUrl(self, obj):
        # Get the request object from the context
        request = self.context.get('request')
        if obj.item.imageUrl:
            return request.build_absolute_uri(obj.item.imageUrl.url)
        return None


class StorePotionSerializer(serializers.ModelSerializer):
    potion = PotionSerializer(many=False, read_only=True)
    class Meta:
        model = models.StorePotion
        fields = '__all__'


class StoreCollectableItemSerializer(serializers.ModelSerializer):
    collectableItem = CollectableItemSerializer(many=False, read_only=True)
    class Meta:
        model = models.StoreCollectableItem
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    
    sellItems = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    buyItems = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = models.Transaction
        fields = ('user', 'store', 'sellItems', 'buyItems', 'totalAmount', 'date')
        read_only_fields = ('totalAmount', 'date')
    

    def validate(self, attrs):
        args = attrs
        user = self.context.get('request').user
        itemsSell = args.pop('sellItems', [])
        itemsBuy = args.pop('buyItems', [])

        sum1 = 0
        sum2 = 0
        
        for i, item in enumerate(itemsSell):
            try:
                sum1 += models.UserItems.objects.filter(user=user).get(id=item).item.goldValue
            except models.UserItems.DoesNotExist:
                raise ValidationError({'error': 'Podano nieprawidłowe id przedmiotów użytkownika'})
        # Sum values of items that user is going to buy
        for i, item in enumerate(itemsBuy):
            try: 
                sum2 += models.StoreItem.objects.filter(store=attrs['store']).get(id=item).price
            except models.StoreItem.DoesNotExist:
                raise ValidationError({'error': 'Podano niepoprawne id przedmiotów ze sklepu'})
        
        total = sum1 - sum2
        args['totalAmount'] = total
        
        if total < 0:
            resurces = models.Resources.objects.get(user=user)
            can_afford = resurces.gold + total

            if can_afford < 0:
                raise ValidationError({'error': 'Niewystarczająca ilość złota'})
            
        for item in itemsSell:
            models.UserItems.objects.get(user=user, id=item).delete()
        for item in itemsBuy:
            itemId = models.StoreItem.objects.get(id=item).item.id
            models.UserItems.objects.create(user=user, item=models.Item.objects.get(id=itemId))
        
        return args
    
    def create(self, validated_data):
        transaction = models.Transaction.objects.create(**validated_data)
        user = self.context.get('request').user
        resources = models.Resources.objects.get(user=user)
        resources.gold += validated_data['totalAmount']
        resources.save()
        return models.Transaction.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.save()
        return instance
    
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = '__all__'

class SubLocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.SubLocation
        fields = '__all__'


class LocationElementSerializer(serializers.ModelSerializer):
    npc = NPCSerializer(read_only=True)
    enemy = EnemySerializer(read_only=True)
    item = ItemSerializer(read_only=True)
    location_element = LocationSerializer(read_only=True)
    sublocation_element = SubLocationSerializer(read_only=True)

    class Meta:
        model = models.LocationElement
        fields = ("type", "position_x", "position_y", "npc", "enemy", "description", "item", "location_element", "sublocation_element")


class SubLocationSerializer(serializers.ModelSerializer):
    elements = LocationElementSerializer(many=True, read_only=True)

    class Meta:
        model = models.SubLocation
        fields = ("id", "name", "description", "imageUrl", "elements", "parent_location")


class LocationSerializer(serializers.ModelSerializer):
    elements = LocationElementSerializer(many=True, read_only=True)

    class Meta:
        model = models.Location
        fields = ('id', 'name', 'description', 'sublocations', 'elements', 'lvlRequired', 'imageUrl', 'region', 'xCoordinate', 'yCoordinate')


class UserLocationSerializer(serializers.ModelSerializer):
    location = LocationSerializer(many=False, read_only=True)
    class Meta:
        model = models.UserLocation
        fields = '__all__'


class TargetObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, models.Enemy):
            return value.name
        elif isinstance(value, models.Item):
            return value.name
        elif isinstance(value, models.Location):
            return value.name
        elif isinstance(value, models.NPC):
            return value.name
        raise Exception('Unexpected type of tagged object')

class QuestRequirementSerializer(serializers.ModelSerializer):

    #target_content_type = TargetObjectRelatedField(read_only=True)
    target = TargetObjectRelatedField(read_only=True)

    class Meta:
        model = models.QuestRequirement
        fields = ('type', 'amount', 'target',
                  'target_content_type', 'target_object_id', 'position', 'path', 'is_last')


class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Quest
        fields = '__all__'


class UserQuestRequirementSerializer(serializers.ModelSerializer):
    requirement = QuestRequirementSerializer(many=False, read_only=True)
    class Meta:
        model = models.UserQuestRequirement
        fields = '__all__'


class UserQuestSerializer(serializers.ModelSerializer):

    quest = QuestSerializer(many=False, read_only=True)
    requirements = UserQuestRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = models.UserQuest
        fields = ('quest', 'requirements', 'progress')


class DialogOptionSerializer(serializers.ModelSerializer):  
    class Meta:
        model = models.DialogOption
        fields = ('id', 'dialog','content', 'next_dialog', 'effects')


class DialogSerializer(serializers.ModelSerializer):

    options = DialogOptionSerializer(many=True, read_only=True)
    npc = NPCSerializer(read_only=True)

    class Meta:
        model = models.Dialog
        fields = ('id', 'npc', 'content', 'event_id', 'options', 'starter')