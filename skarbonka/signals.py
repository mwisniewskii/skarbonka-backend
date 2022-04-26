# Standard Library
import datetime
from datetime import timedelta

# Django
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

# 3rd-party
from django_celery_beat.models import ClockedSchedule
from django_celery_beat.models import PeriodicTask

# Project
from accounts.models import ControlType, UserType

# Local
from .enum import LoanStatus
from .enum import NotificationType
from .enum import TransactionStatus
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
def transaction_status(sender, instance, **kwargs):

    if instance.sender is not None:
        if instance.sender.parental_control == ControlType.CONFIRMATION:
            instance.status = TransactionStatus.PENDING
        if instance.sender.balance < instance.amount:
            instance.status = TransactionStatus.FAILED


@receiver(post_save, sender=Transaction)
def transaction_confirmation_notification(sender, instance, created, **kwargs):
    if instance.sender is not None:
        control_type = instance.sender.parental_control == ControlType.CONFIRMATION
        status = instance.status == TransactionStatus.PENDING
        if control_type and status and created:
            notifications = []
            for parent in instance.sender.family.parents:
                notifications.append(
                    Notification(
                        recipient=parent,
                        content=f"{instance.sender} chcę dokonać transakcji na kwotę {instance.amount}",
                        resource=NotificationType.WITHDRAW,
                        target=instance.id,
                    )
                )
            Notification.objects.bulk_create(notifications)


@receiver(post_save, sender=Loan)
def loans_notifications_transactions(sender, instance, created, **kwargs):
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
                args=[instance.payment_date, recipient.id, instance.id],
                start_time=timezone.now(),
            )
            instance.save()

        elif instance.status == LoanStatus.DECLINED:
            msg = f'Pożyczka na kwotę {instance.amount} została odrzucona.'
            recipient = instance.borrower

        elif instance.status == LoanStatus.PAID:
            msg = f'{instance.borrower} spłacił pożyczkę z terminem spłaty do {instance.payment_date}.'
            recipient = instance.lender
            instance.notify.delete()
        else:
            return
        Notification.objects.create(
            recipient=recipient,
            content=msg,
            resource=NotificationType.LOAN,
            target=instance.id,
        )
