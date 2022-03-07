from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    USERNAME_FIELD = 'email'
    email = models.EmailField(
        verbose_name="email address", unique=True,
        error_messages={
            'unique':
                "A user is already registered with this email address",
        },
    )
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()

    def __str__(self):
        return self.email
