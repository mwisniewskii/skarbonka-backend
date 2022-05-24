# Django
from django.db import models


class TransactionType(models.IntegerChoices):
    ORDINARY = 1, 'Ordinary'
    DEPOSIT = 2, 'Deposit'
    WITHDRAW = 3, 'Withdraw'
    LOAN = 4, 'Loan'
    ALLOWANCE = 5, 'Allowance'


class TransactionState(models.TextChoices):
    ACCEPTED = 1, 'Accepted'
    PENDING = 2, 'Pending'
    FAILED = 3, 'Failed'
    DECLINED = 4, 'Declined'
    TO_CONFIRM = 5, 'Require Confirmation'


class FrequencyType(models.IntegerChoices):
    DAILY = 1, 'Daily'
    WEEKLY = 2, 'Weekly'
    MONTHLY = 3, 'Monthly'


class LoanState(models.IntegerChoices):
    PENDING = 1, 'Pending'
    GRANTED = 2, 'Granted'
    DECLINED = 3, 'Declined'
    PAID = 4, 'Paid off'
    EXPIRED = 5, 'Expired'
