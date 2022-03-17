# Django
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum

from skarbonka.models import Transaction

# Local
from .managers import CustomUserManager


class Family(models.Model):
    """Aggregation of family members."""

    name = models.CharField(max_length=255)


class CustomUser(AbstractUser):
    """Custom user model with e-mail as unique identifiers."""

    class UserType(models.IntegerChoices):
        PARENT = 1, "Parent"
        CHILD = 2, "Child"

    class ControlType(models.IntegerChoices):
        NONE = 1, "None"
        CONFIRMATION = 2, "Confirmation"
        PERIODIC = 3, "Periodic limit"

    username = None
    email = models.EmailField(
        verbose_name="email address",
        unique=True,
        error_messages={
            "unique": "A user is already registered with this email address",
        },
    )
    family = models.ForeignKey(Family, null=True, on_delete=models.CASCADE)
    user_type = models.PositiveSmallIntegerField(choices=UserType.choices, default=UserType.PARENT)
    parental_control = models.PositiveSmallIntegerField(
        choices=ControlType.choices, default=ControlType.NONE
    )
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = CustomUserManager()

    @property
    def get_balance(self):
        income = Transaction.objects.filter(recipient=self).aggregate(Sum('amount'))
        outcome = Transaction.objects.filter(sender=self).aggregate(Sum('amount'))
        return income - outcome

    def __str__(self):  # noqa: D105
        return self.email
