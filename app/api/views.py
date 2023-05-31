from rest_framework import viewsets, mixins, generics, authentication, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError

from api import models
from api import serializers


class BaseViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def partial_update(self, request, *args, **kwargs):
        # Do something with the partial update data
        return super().partial_update(request, *args, **kwargs)


class ResourceViewSet(BaseViewSet):
    queryset = models.Resources.objects.all()
    serializer_class = serializers.ResourcesSerializer

    def get_queryset(self):
        return models.Resources.objects.filter(user=self.request.user)


class CreateUserView(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': user.name,
            'email': user.email,
            'id': user.id
        })


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
    

class CharacterViewSet(BaseViewSet):
    serializer_class = serializers.CharacterSerializer
    queryset = models.Character.objects.all()

    def get_queryset(self):
        return models.Character.objects.filter(user=self.request.user)


class ItemViewSet(BaseViewSet):
    serializer_class = serializers.ItemSerializer
    queryset = models.Item.objects.all()


class CharacterItemViewSet(BaseViewSet):
    serializer_class = serializers.CharacterItemSerializer
    queryset = models.CharacterItem.objects.all()
    lookup_field = 'slot'

    def get_queryset(self):
        character = models.Character.objects.get(user=self.request.user)
        return models.CharacterItem.objects.filter(character=character)


class UserItemViewSet(BaseViewSet):
    serializer_class = serializers.UserItemsSerializer
    queryset = models.UserItems.objects.all()

    def get_queryset(self):
        return models.UserItems.objects.filter(user=self.request.user)    


class EnemyViewSet(BaseViewSet):
    serializer_class = serializers.EnemySerializer
    queryset = models.Enemy.objects.all()
    http_method_names = ['get']

class EnemyLootViewSet(BaseViewSet):
    serializer_class = serializers.EnemyLootSerializer
    queryset = models.EnemyLoot.objects.all()
    lookup_field = 'enemy'
    http_method_names = ['get']


class LocationViewSet(BaseViewSet):
    serializer_class = serializers.LocationSerializer
    queryset = models.Location.objects.all()
    http_method_names = ['get']


class UserLocationViewSet(BaseViewSet):
    serializer_class = serializers.UserLocationSerializer
    queryset = models.UserLocation.objects.all()

    def get_queryset(self):
        return models.UserLocation.objects.filter(user=self.request.user)


class StoreViewSet(BaseViewSet):
    serializer_class = serializers.StoreSerializer
    queryset = models.Store.objects.all()
    http_method_names = ['get']

    def get_queryset(self):
        location = models.UserLocation.objects.get(user=self.request.user)
        return models.Store.objects.filter(location=location.location)


class StoreItemViewSet(BaseViewSet):
    serializer_class = serializers.StoreItemSerializer
    queryset = models.StoreItem.objects.all()
    lookup_field = 'store'
    http_method_names = ['get']


class InventoryViewSet(BaseViewSet):
    serializer_class = serializers.UserItemsSerializer
    serializer_classes = {
        'items': serializers.UserItemsSerializer,
        'potions': serializers.UserPotionsSerializer,
        'collectableItems': serializers.UserCollectableItemsSerializer,
    }
    queryset = models.UserItems.objects.all()

    

    def list(self, reqeust):
        user = reqeust.user
        items = models.UserItems.objects.filter(user=user)
        potions = models.UserPotions.objects.filter(user=user)
        collectable = models.UserCollectableItem.objects.filter(user=user)
    
        item_serializer = self.serializer_classes['items'](items, many=True)
        potion_serializer = self.serializer_classes['potions'](potions, many=True)
        collectable_serializer = self.serializer_classes['collectableItems'](collectable, many=True)

        data = {
            'items': item_serializer.data,
            'potions': potion_serializer.data,
            'collectableItems': collectable_serializer.data
        }

        return Response(data)