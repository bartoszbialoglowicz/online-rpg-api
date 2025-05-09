from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register('resources', views.ResourceViewSet)
router.register('character', views.CharacterViewSet)
router.register('item', views.ItemViewSet)
router.register(r'equipment', views.CharacterItemViewSet)
router.register('useritems', views.UserItemViewSet)
router.register('enemies', views.EnemyViewSet)
router.register('enemy_loot', views.EnemyLootViewSet)
router.register('locations', views.LocationViewSet)
router.register('current_location', views.UserLocationViewSet)
router.register('store', views.StoreViewSet)
router.register('storeitems', views.StoreItemViewSet)
router.register('inventory', views.InventoryViewSet)
router.register('transaction', views.TransactionViewSet)
router.register('quests', views.UserQuestViewSet)
router.register('dialogs', views.DialogViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('createuser/', views.CreateUserView.as_view(), name='createuser'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

