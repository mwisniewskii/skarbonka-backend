# Django
from django.apps import AppConfig


class SkarbonkaConfig(AppConfig):
    """Register config in skarbonka app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "skarbonka"

    def ready(self):
        from skarbonka import signals