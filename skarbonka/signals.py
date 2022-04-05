# Django
from django.db.models.signals import post_save
from django.dispatch import receiver

# Local
from .models import Allowance


@receiver(post_save, sender=Allowance)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()
