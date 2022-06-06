# Django
from django.db.models.signals import post_save
from django.dispatch import receiver

# Local
from .models import Allowance
from .models import Loan
from .models import Notification


@receiver(post_save, sender=Allowance)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


@receiver(post_save, sender=Loan)
def loans_notifications_transactions(sender, instance, created, **kwargs):
    """Signals for handle loan status."""
    if created:
        msg = f'{instance.borrower} prosi cię o pożyczkę na {instance.amount}.'
        recipient = instance.lender
        Notification.objects.create(
            recipient=recipient,
            content=msg,
        )
