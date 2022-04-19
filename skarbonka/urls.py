# Standard Library
import platform

# Django
from django.urls import path

# Local
from .views import AllowanceViewSet
from .views import DepositViewSet
from .views import LoanPayoffViewSet
from .views import LoanViewSet
from .views import NotificationViewSet

allowanceList = AllowanceViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)
allowanceDetail = AllowanceViewSet.as_view(
    {
        "get": "retrieve",
        "patch": "partial_update",
        "delete": "destroy",
    }
)
notificationsList = NotificationViewSet.as_view(
    {
        "get": "list",
    }
)
loanList = LoanViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)
loanDetail = LoanViewSet.as_view(
    {
        "get": "retrieve",
        "patch": "partial_update",
    }
)
userDeposit = DepositViewSet.as_view(
    {
        "post": "create",
    }
)
loanPayoff = LoanPayoffViewSet.as_view(
    {
        "post": "create",
    }
)
urlpatterns = [
    path("allowances/", allowanceList, name="allowances"),
    path("allowances/<int:pk>/", allowanceDetail, name="allowance"),
    path("notifications/", notificationsList, name="notification"),
    path("loans/", loanList, name="loans"),
    path("loans/<int:pk>/", loanDetail, name="loan"),
    path("deposit/", userDeposit, name="deposits"),
    path("loans/<int:loan_id>/pay-off/", loanPayoff, name="loanpayoff"),
]
