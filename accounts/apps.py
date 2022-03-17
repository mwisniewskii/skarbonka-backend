# Django
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Register config of accounts app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
