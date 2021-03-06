# Standard Library
import datetime

# Django
from django.utils import timezone

# Project
from accounts.enum import ControlType
from skarbonka.enum import TransactionType


def is_ordinary_transaction(instance):
    return instance.types == TransactionType.ORDINARY


def sender_funds_enough(instance):
    if instance.sender:
        return instance.amount <= instance.sender.balance
    return True


def period_limit_check(instance):
    if instance.sender:
        if instance.sender.parental_control == ControlType.PERIODIC:
            period = timezone.datetime.now() - datetime.timedelta(
                days=instance.sender.days_limit_period
            )
            return (
                instance.sender.outcome(period) + instance.amount
                <= instance.sender.sum_periodic_limit
            )
    return True


def confirmation_control(instance):
    if instance.sender:
        return instance.sender.parental_control == ControlType.CONFIRMATION
    return False


def loan_funds_enough(instance):
    return instance.lender.balance >= instance.amount


def is_paid(instance):
    return instance.amount <= instance.paid
