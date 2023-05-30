from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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
                        message="Provided email is already in use."
                    ),
                ]
            },
            'name': {
                'validators': [
                    UniqueValidator(
                        queryset=get_user_model().objects.all(),
                        message="Provided nickname is already in use."
                    ),
                ]
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create(**validated_data)
    
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


class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Resources
        fields = '__all__'


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Character
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Item
        fields = '__all__'


class CharacterItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False, read_only=True)
    class Meta:
        model = models.CharacterItem
        fields = ('slot', 'item')


class UserItemsSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=True, read_only=True)
    class Meta:
        model = models.UserItems
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


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = '__all__'


class UserLocationSerializer(serializers.ModelSerializer):
    location = LocationSerializer(many=False, read_only=True)
    class Meta:
        model = models.UserLocation
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Store
        fields = '__all__'


class StoreItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StoreItem
        fields = '__all__'
