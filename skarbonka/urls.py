# Django
from django.urls import path

# Local
from .views import AllowanceViewSet
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

urlpatterns = [
    path("allowances/", allowanceList, name="allowances"),
    path("allowances/<int:pk>/", allowanceDetail, name="allowance"),
    path("notifications/", notificationsList, name="notification"),
]
