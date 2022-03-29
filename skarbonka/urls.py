# Django
from django.urls import path

# Local
from .views import DepositViewSet

usertDeposit = DepositViewSet.as_view(
    {
        "post": "create",
    }
)

urlpatterns = [
    path("deposit/", usertDeposit, name="deposits"),
]
