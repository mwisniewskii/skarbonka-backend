# Standard Library
from datetime import timedelta

# Django
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

# 3rd-party
from django_celery_beat.models import ClockedSchedule
from django_celery_beat.models import PeriodicTask

# Local
from .enum import LoanStatus
from .enum import NotificationType
from .enum import TransactionType
from .models import Allowance
from .models import Loan
from .models import Notification
from .models import Transaction


@receiver(post_save, sender=Allowance)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


@receiver(pre_save, sender=Transaction)
def transaction_faild(sender, instance, **kwargs):
    if instance.sender is not None:
        instance.faild = instance.sender.balance < instance.amount


@receiver(post_save, sender=Loan)
def loans_notifications_transactions(sender, update_fields, instance, created, **kwargs):
    """Signals for handle loan status."""
    if created:
        msg = f'{instance.borrower} prosi cię o pożyczkę na {instance.amount}.'
        recipient = instance.lender
        Notification.objects.create(
            recipient=recipient,
            content=msg,
            resource=NotificationType.LOAN,
            target=instance.id,
        )
    elif instance.status_tracker.changed():
        if instance.status == LoanStatus.GRANTED:
            msg = f'Pożyczka na kwotę {instance.amount} została przyznana, termin jej spłaty to {instance.payment_date}'
            recipient = instance.borrower
            Transaction.objects.create(
                sender=instance.lender,
                recipient=instance.borrower,
                title=f'Pożyczka od {instance.lender} dla {instance.borrower}',
                amount=instance.amount,
                types=TransactionType.LOAN,
            )
            instance.notify = PeriodicTask.objects.create(
                name=f'Payment notify {instance.pk} ',
                task='admit_allowance',
                clocked=ClockedSchedule.objects.create(
                    clocked_time=instance.payment_date - timedelta(7)
                ),
                args=[],
                start_time=timezone.now(),
            )
            instance.save()

        elif instance.status == LoanStatus.DECLINED:
            msg = f'Pożyczka na kwotę {instance.amount} została odrzucona.'
            recipient = instance.borrower

        elif instance.status == LoanStatus.PAID:
            msg = _(f'{instance.borrower} spłacił pożyczkę z terminem spłaty do {instance.payment_date}.')
            recipient = instance.lender
            instance.notify.delete()

        Notification.objects.create(
            recipient=recipient,
            content=msg,
            resource=NotificationType.LOAN,
            target=instance.id,
        )
