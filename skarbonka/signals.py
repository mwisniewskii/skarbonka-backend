# Django
from django.db.models.signals import post_save
from django.dispatch import receiver

# Local
from django_celery_beat.models import ClockedSchedule

from .models import Allowance, Loan, Notification, LoanStatus, NotificationType, Transaction, TransactionType


@receiver(post_save, sender=Allowance)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


@receiver(post_save, sender=Loan)
def loans_notifications_transactions(sender, update_fields, instance, created, **kwargs):
    """Signals for handle loan status."""
    if 'status' in update_fields:
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
            instance.notify = ClockedSchedule.objects.create(
                clocked_time=instance.payment_date
            )

        elif instance.status == LoanStatus.DECLINED:
            msg = f'Pożyczka na kwotę {instance.amount} została odrzucona.'
            recipient = instance.borrower
        elif instance.status == LoanStatus.PAID:
            msg = f'{instance.borrower} społcił pożyczkę której termin spłaty był do {instance.payment_date}.'
            recipient = instance.lender
        else:
            msg = f'{instance.borrower} prosi cię o pożyczkę na {instance.amount}.'
            recipient = instance.lender

        Notification.objects.create(
                recipient=recipient,
                content=msg,
                resource=NotificationType.LOAN,
                target=instance.id,
        )

