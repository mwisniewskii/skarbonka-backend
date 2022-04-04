from celery import shared_task

from accounts.models import CustomUser

from .models import Transaction, TransactionType


@shared_task(name='admit_allowance')
def admit_allowance(sender_id, recipient_id, amount):
    sender = CustomUser.objects.get(pk=sender_id)
    if sender.balance >= amount:
        Transaction.objects.create(
            sender_id=sender_id,
            recipient_id=recipient_id,
            title="Kieszonkowe",
            amount=amount,
            types=TransactionType.ALLOWANCE,
        )
    else:
        print("wielka bieda")
