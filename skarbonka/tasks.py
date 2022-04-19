# Standard Library
from datetime import timedelta

# Django
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# 3rd-party
from celery import shared_task
from django_celery_beat.models import ClockedSchedule
from django_celery_beat.models import PeriodicTask

# Project
from accounts.models import CustomUser

# Local
from .enum import LoanStatus
from .enum import NotificationType
from .enum import TransactionType
from .models import Loan
from .models import Notification
from .models import Transaction


@shared_task(name='admit_allowance')
def admit_allowance(sender_id, recipient_id, amount):
    sender = CustomUser.objects.get(pk=sender_id)
    recipient = CustomUser.objects.get(pk=recipient_id)
    transaction = Transaction.objects.create(
        sender_id=sender_id,
        recipient_id=recipient_id,
        title=f'Kieszonkowe od {sender} dla {recipient}',
        amount=amount,
        types=TransactionType.ALLOWANCE,
    )
    if transaction.failed:
        Notification.objects.create(
            recipient=sender,
            content=f'Nie udało się przelać kieszonkowego dla {recipient}',
            resource=NotificationType.TRANSACTION,
            target=transaction.id,
        )


@shared_task(name='loan_payment_date_notification')
def loan_payment_date_notification(payment_date, borrower_id, loan_id):
    days_to_pay = payment_date - timezone.now()

    notify_days = days_to_pay.days / 2
    loan = Loan.objects.get(id=loan_id)
    if notify_days > 0:
        msg = f'Za {days_to_pay.days} dni upływa termin spłaty pożyczki.'
        clocked_time = payment_date - timedelta(notify_days)
    elif notify_days == 0:
        msg = f'Minął termin spłaty pożyczki.'
        clocked_time = payment_date
        loan.status = LoanStatus.EXPIRED
    else:
        return

    loan.notify = PeriodicTask.objects.create(
        name=f'Payment notify {loan_id} {payment_date}',
        task='loan_payment_date_notification',
        clocked=ClockedSchedule.objects.create(clocked_time=clocked_time),
        args=[payment_date, borrower_id, loan_id],
        start_time=timezone.now(),
    )
    loan.save()
    Notification.objects.create(
        recipient_id=borrower_id,
        content=msg,
        resource=NotificationType.LOAN,
        target=loan_id,
    )
