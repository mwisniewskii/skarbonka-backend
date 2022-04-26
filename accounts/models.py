# Standard Library
import datetime

# Django
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.db.models import Sum

# Project
from skarbonka.enum import TransactionStatus
from skarbonka.models import Transaction

# Local
from .managers import CustomUserManager


class ControlType(models.IntegerChoices):
    NONE = 1, "None"
    CONFIRMATION = 2, "Confirmation"
    PERIODIC = 3, "Periodic limit"


class UserType(models.IntegerChoices):
    PARENT = 1, "Parent"
    CHILD = 2, "Child"


class Family(models.Model):
    """Aggregation of family members."""

    name = models.CharField(max_length=255)

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
            date_from = datetime.datetime.now() - datetime.timedelta(days=10 * 365)
        income = Transaction.objects.filter(
            status=TransactionStatus.ACCEPTED,
            recipient=self,
            datetime__gt=date_from,
        ).aggregate(Sum('amount'))
        return income['amount__sum'] or 0

    def outcome(self, date_from=None):
        if not date_from:
            date_from = datetime.datetime.now() - datetime.timedelta(days=10 * 365)
        outcome = Transaction.objects.filter(
            Q(status=TransactionStatus.ACCEPTED) | Q(status=TransactionStatus.PENDING),
            sender=self,
            datetime__gt=date_from,
        ).aggregate(Sum('amount'))
        return outcome['amount__sum'] or 0

    @property
    def balance(self):
        return self.income() - self.outcome()

    def __str__(self):  # noqa: D105
        return f'{self.first_name} {self.last_name}'
