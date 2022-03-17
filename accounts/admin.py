# Django
from django.contrib import admin

# Local
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """UserProfile admin."""

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "date_joined",
    )
    search_fields = ("email",)
