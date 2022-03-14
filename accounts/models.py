# Django
from django.contrib.auth.models import AbstractUser
from django.db import models

# Local
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    """Custom user model with e-mail as unique identifiers."""

    username = None
    USERNAME_FIELD = 'email'
    email = models.EmailField(
        verbose_name='email address', unique=True,
        error_messages={
            'unique':
                'A user is already registered with this email address',
        },
    )
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()

    def __str__(self):  # noqa: D105
        return self.email
