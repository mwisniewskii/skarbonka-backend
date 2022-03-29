# Django
from django.urls import path

# Local
from .views import AllowanceViewSet

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


urlpatterns = [
    path("allowances/", allowanceList, name="allowances"),
    path("allowances/<int:pk>/", allowanceDetail, name="allowance"),
]
