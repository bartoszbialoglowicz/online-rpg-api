from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from api import models

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


admin.site.register(models.Resources)
admin.site.register(models.CustomUser, UserAdmin)
admin.site.register(models.Character)
admin.site.register(models.UserItems)
admin.site.register(models.UserPotions)
admin.site.register(models.UserCollectableItem)
admin.site.register(models.CharacterItem)
admin.site.register(models.Item)
admin.site.register(models.Potion)
admin.site.register(models.CollectableItem)
admin.site.register(models.Enemy)
admin.site.register(models.EnemyLoot)
admin.site.register(models.Region)
admin.site.register(models.Location)
admin.site.register(models.UserLocation)
admin.site.register(models.Store)
admin.site.register(models.StoreItem)
admin.site.register(models.StorePotion)
admin.site.register(models.StoreCollectableItem)
