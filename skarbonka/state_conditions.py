import datetime

from accounts.models import ControlType
from skarbonka.enum import TransactionType


def is_ordinary_transaction(self):
    return self.types == TransactionType.ORDINARY


def sender_funds_enough(self):
    if self.sender:
        return self.amount <= self.sender.balance
    return True


def period_limit_check(self):
    if self.sender.parental_control == ControlType.PERIODIC:
        period = datetime.datetime.now() - datetime.timedelta(days=self.sender.days_limit_period)
        return self.sender.outcome(period) >= self.sender.sum_periodic_limit