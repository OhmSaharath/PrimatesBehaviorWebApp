# apps.py or models.py or signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RPiStates
from .channels_utils import broadcast_state

@receiver(post_save, sender=RPiStates)
def send_state_update(sender, instance, **kwargs):
    broadcast_state(instance)