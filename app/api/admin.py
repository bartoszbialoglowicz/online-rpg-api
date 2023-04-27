from django.contrib import admin

from api import models


admin.site.register(models.Resources)
admin.site.register(models.CustomUser)
admin.site.register(models.Character)
admin.site.register(models.UserItems)
admin.site.register(models.CharacterItem)
admin.site.register(models.Item)
admin.site.register(models.Enemy)