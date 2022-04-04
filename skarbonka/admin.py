from django.contrib import admin

from .models import Allowance, Transaction


@admin.register(Allowance)
class CustomAllowanceAdmin(admin.ModelAdmin):
    """UserProfile admin."""


@admin.register(Transaction)
class CustomTransactionAdmin(admin.ModelAdmin):
    """UserProfile admin."""
