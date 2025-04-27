# api/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Location, Region

@receiver(post_migrate)
def create_default_location(sender, **kwargs):
    try:
        Location.objects.get(name="Przełęcz Mroźnego Wiatru")
    except Location.DoesNotExist:
        default_region, _ = Region.objects.get_or_create(
            name="Default", 
            defaults={"description": "Default region"})
        Location.objects.create(
            name="Przełęcz Mroźnego Wiatru",
            region=default_region,
            lvlRequired=1,
            description="Domyślna lokalizacja",
            xCoordinate=0,
            yCoordinate=0,
        )
