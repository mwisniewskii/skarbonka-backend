# Django
from django.urls import path

# Local
from .views import AllowanceViewSet
from .views import DepositViewSet
from .views import LoanPayoffViewSet
from .views import LoanViewSet
from .views import NotificationViewSet
from .views import TransactionUpdateView
from .views import TransactionViewSet
from .views import WithdrawViewSet

allowanceList = AllowanceViewSet.as_view({"get": "list", "post": "create"})
allowanceDetail = AllowanceViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)


userTransactionList = TransactionViewSet.as_view({"get": "list", "post": "create"})
transactionDetail = TransactionUpdateView.as_view({"get": "retrieve", "patch": "partial_update"})
notificationsList = NotificationViewSet.as_view({"get": "list"})
loanList = LoanViewSet.as_view({"get": "list", "post": "create"})
loanDetail = LoanViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
userDeposit = DepositViewSet.as_view({"post": "create"})
loanPayoff = LoanPayoffViewSet.as_view({"post": "create"})
withdraw = WithdrawViewSet.as_view({"post": "create"})
withdrawDetail = WithdrawViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
withdraws = WithdrawViewSet.as_view({"get": "list"})


urlpatterns = [
    path("allowances/", allowanceList, name="allowances"),
    path("allowances/<int:pk>/", allowanceDetail, name="allowance"),
    path("notifications/", notificationsList, name="notification"),
    path("transaction/", userTransactionList, name="transactions"),
    path("transaction/<int:pk>/", transactionDetail, name="transaction"),
    path("loans/", loanList, name="loans"),
    path("loans/<int:pk>/", loanDetail, name="loan"),
    path("deposit/", userDeposit, name="deposits"),
    path("loans/<int:loan_id>/pay-off/", loanPayoff, name="loanpayoff"),
    path("withdraw/", withdraw, name="withdraw"),
    path("users/<int:user_id>/withdraws/", withdraws, name="withdraws"),
    path("users/<int:user_id>/withdraws/<int:pk>", withdrawDetail, name="withdraws-detail"),
]
