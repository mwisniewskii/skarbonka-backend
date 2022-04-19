# Django
from django.db import models


class TransactionType(models.IntegerChoices):
    ORDINARY = 1, 'Ordinary'
    DEPOSIT = 2, 'Deposit'
    WITHDRAW = 3, 'Withdraw'
    LOAN = 4, 'Loan'
    ALLOWANCE = 5, 'Allowance'


class FrequencyType(models.IntegerChoices):
    DAILY = 1, 'Daily'
    WEEKLY = 2, 'Weekly'
    MONTHLY = 3, 'Monthly'


class NotificationType(models.IntegerChoices):
    NONE = 1, 'None'
    TRANSACTION = 2, 'Transaction'
    ALLOWANCE = 3, 'Allowance'
    LOAN = 4, 'Loan'


class LoanStatus(models.IntegerChoices):
    PENDING = 1, 'Pending'
    GRANTED = 2, 'Granted'
    DECLINED = 3, 'Declined'
    PAID = 4, 'Paid off'
    EXPIRED = 5, 'Expired'
