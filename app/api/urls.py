from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register('resources', views.ResourceViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('createuser/', views.CreateUserView.as_view(), name='createuser'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me')
]
