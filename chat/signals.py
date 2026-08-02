from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Room


@receiver(post_save, sender=User)
def generate_keys(sender, instance, created, **kwargs):
    if created:
        instance.generate_key_pair()


@receiver(post_save, sender=Room)
def generate_shared_key(sender, instance, created, **kwargs):
    if created:
        instance.generate_shared_key()