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
    