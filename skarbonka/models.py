from django.db import models


class TransactionType(models.IntegerChoices):
    ORDINARY = 1, 'Ordinary'
    DEPOSIT = 2, 'Deposit'
    WITHDRAW = 3, 'Withdraw'
    LOAN = 4, 'Loan'


class Transaction(models.Model):
    """Models of user transactions."""

    sender = models.ForeignKey(
        'accounts.CustomUser', null=True, on_delete=models.SET_NULL, related_name='sender'
    )
    recipient = models.ForeignKey(
        'accounts.CustomUser', null=True, on_delete=models.SET_NULL, related_name='recipient'
    )
    datetime = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    types = models.PositiveSmallIntegerField(
        choices=TransactionType.choices, default=TransactionType.ORDINARY
    )
