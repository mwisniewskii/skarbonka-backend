# Django
from django.contrib.auth.models import AbstractUser
from django.db import models

# Local
from .managers import CustomUserManager


class Family(models.Model):
    """Aggregation of family members."""

    name = models.CharField(max_length=255)


class CustomUser(AbstractUser):
    """Custom user model with e-mail as unique identifiers."""

    USER_TYPE = (
        (1, 'Parent'),
        (2, 'Child'),
    )
    CONTROL_TYPE = (
        (1, 'None'),
        (2, 'Confirmation'),
        (3, 'Periodic limit'),
    )

    username = None
    email = models.EmailField(
        verbose_name='email address', unique=True,
        error_messages={
            'unique':
                'A user is already registered with this email address',
        },
    )
    family = models.ForeignKey(Family, null=True, on_delete=models.CASCADE)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE, default=1)
    parental_control = models.PositiveSmallIntegerField(choices=CONTROL_TYPE, default=1)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()

    def __str__(self):  # noqa: D105
        return self.email
