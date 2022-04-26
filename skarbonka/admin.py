# Django
from django.contrib import admin

# Local
from .models import Allowance
from .models import Loan
from .models import Notification
from .models import Transaction


@admin.register(Allowance)
class CustomAllowanceAdmin(admin.ModelAdmin):
    """UserProfile admin."""


@admin.register(Transaction)
class CustomTransactionAdmin(admin.ModelAdmin):
    """UserProfile admin."""


@admin.register(Loan)
class CustomLoanAdmin(admin.ModelAdmin):
    """UserProfile admin."""


@admin.register(Notification)
class CustomLoanAdmin(admin.ModelAdmin):
    """UserProfile admin."""
