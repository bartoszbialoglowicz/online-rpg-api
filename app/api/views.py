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
