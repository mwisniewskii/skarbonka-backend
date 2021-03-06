# Standard Library
import datetime

# Django
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.utils import timezone

# Project
from skarbonka.enum import TransactionState
from skarbonka.models import Transaction

# Local
from .enum import ControlType
from .enum import UserType
from .managers import CustomUserManager


class Family(models.Model):
    """Aggregation of family members."""

    @property
    def parents(self):
        return self.family.filter(user_type=UserType.PARENT)

    @property
    def children(self):
        return self.family.filter(user_type=UserType.CHILD)


class CustomUser(AbstractUser):
    """Custom user model with e-mail as unique identifiers."""

    username = None
    email = models.EmailField(
        verbose_name="email address",
        unique=True,
        error_messages={
            "unique": "A user is already registered with this email address",
        },
    )
    family = models.ForeignKey(Family, null=True, on_delete=models.CASCADE, related_name='family')
    user_type = models.PositiveSmallIntegerField(choices=UserType.choices, default=UserType.PARENT)
    parental_control = models.PositiveSmallIntegerField(
        choices=ControlType.choices, default=ControlType.NONE
    )
    days_limit_period = models.PositiveIntegerField(null=True, blank=True)
    sum_periodic_limit = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = CustomUserManager()

    def income(self, date_from=None):
        if not date_from:
            date_from = timezone.now() - datetime.timedelta(days=10 * 365)
        income = Transaction.objects.filter(
            state=TransactionState.ACCEPTED,
            recipient=self,
            datetime__gt=date_from,
        ).aggregate(Sum('amount'))
        return income['amount__sum'] or 0

    def outcome(self, date_from=None):
        if not date_from:
            date_from = timezone.now() - datetime.timedelta(days=10 * 365)
        outcome = Transaction.objects.filter(
            state=TransactionState.ACCEPTED,
            sender=self,
            datetime__gt=date_from,
        ).aggregate(Sum('amount'))
        return outcome['amount__sum'] or 0

    @property
    def balance(self):
        return self.income() - self.outcome()

    def __str__(self):  # noqa: D105
        return f'{self.first_name} {self.last_name}'
