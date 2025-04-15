from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType

from django import forms
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


class QuestRequirementForm(forms.ModelForm):
    class Meta:
        model = models.QuestRequirement
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and getattr(self.instance, "target_content_type_id", None):
            model_class = self.instance.target_content_type.model_class()
            if model_class:
                self.fields["target_object_id"].queryset = model_class.objects.all()
        else:
            self.fields["target_object_id"].queryset = ContentType.objects.none()




class QuestRequirementAdmin(admin.ModelAdmin):
    form = QuestRequirementForm
    list_display = ("quest", "type", "target_content_type", "target_object_id")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "target_content_type":
            kwargs["queryset"] = ContentType.objects.filter(model__in=["enemy", "item", "location", "npc"])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
admin.site.register(models.NPC)
admin.site.register(models.Location)
admin.site.register(models.SubLocation)
admin.site.register(models.LocationElement)
admin.site.register(models.UserLocation)
admin.site.register(models.Store)
admin.site.register(models.StoreItem)
admin.site.register(models.StorePotion)
admin.site.register(models.StoreCollectableItem)
admin.site.register(models.UserLvl)
admin.site.register(models.Quest)
admin.site.register(models.QuestRequirement, QuestRequirementAdmin)
admin.site.register(models.UserQuest)
admin.site.register(models.UserQuestRequirement)
admin.site.register(models.Dialog)
admin.site.register(models.DialogOption)
