# 3rd-party
from celery import shared_task

# Project
from accounts.models import CustomUser

# Local
from .models import Notification
from .models import NotificationType
from .models import Transaction
from .models import TransactionType


@shared_task(name='admit_allowance')
def admit_allowance(sender_id, recipient_id, amount):
    sender = CustomUser.objects.get(pk=sender_id)
    recipient = CustomUser.objects.get(pk=recipient_id)
    transfer_failed = sender.balance < amount
    transaction = Transaction.objects.create(
        sender_id=sender_id,
        recipient_id=recipient_id,
        title=f'Kieszonkowe od {sender} dla {recipient}',
        amount=amount,
        types=TransactionType.ALLOWANCE,
        failed=transfer_failed,
    )
    if transfer_failed:
        Notification.objects.create(
            recipient=sender,
            content=f'Nie udało się przelać kieszonkowego dla {recipient}',
            resource=NotificationType.TRANSACTION,
            target=transaction.id,
        )
