# Django
from django.urls import path

# Local
from .views import AllowanceViewSet
from .views import NotificationViewSet
from .views import TransactionViewSet

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
userTransactionList = TransactionViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

urlpatterns = [
    path("allowances/", allowanceList, name="allowances"),
    path("allowances/<int:pk>/", allowanceDetail, name="allowance"),
    path("notifications/", notificationsList, name="notification"),
    path("transaction/", userTransactionList, name="transaction"),
]
