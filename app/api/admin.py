from django.contrib import admin

from api import models


admin.site.register(models.Resources)
admin.site.register(models.CustomUser)
admin.site.register(models.Character)
admin.site.register(models.UserItems)
admin.site.register(models.CharacterItem)
admin.site.register(models.Item)
admin.site.register(models.Enemy)
admin.site.register(models.EnemyLoot)
admin.site.register(models.Region)
admin.site.register(models.Location)
admin.site.register(models.UserLocation)
admin.site.register(models.Store)
admin.site.register(models.StoreItem)