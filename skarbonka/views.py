# Django
from django.db.models import Q
from django.http import QueryDict
from django.utils.decorators import method_decorator

# 3rd-party
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Project
from accounts.models import CustomUser, ControlType
from accounts.models import UserType
from accounts.permissions import ParentCUDPermissions

# Local
from .enum import TransactionType
from .models import Allowance
from .models import Loan
from .models import Notification
from .permissions import AuthenticatedPermissions
from .permissions import ChildCreatePermissions
from .permissions import FamilyAllowancesPermissions
from .permissions import LoanObjectPermissions
from .serializers import AllowanceSerializer
from .serializers import CreateWithdrawSerializer
from .serializers import DepositSerializer
from .serializers import LoanChildSerializer
from .serializers import LoanParentSerializer
from .serializers import LoanPayoffSerializer
from .serializers import NotificationSerializer
from .serializers import WithdrawSerializer
from .swagger_schemas import loan_schema
from .utils import period_limit_check


class AllowanceViewSet(viewsets.ModelViewSet):
    """Child allowances."""

    serializer_class = AllowanceSerializer
    permission_classes = (ParentCUDPermissions, FamilyAllowancesPermissions)

    def get_queryset(self):
        user = self.request.user
        if user.user_type == UserType.PARENT:
            return Allowance.objects.filter(parent=user)
        return Allowance.objects.filter(child=user)

    def perform_create(self, serializer):
        serializer.save(parent=self.request.user)

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        instance = self.get_object()
        instance.task.crontab = instance.interval
        instance.task.args = [instance.parent.pk, instance.child.pk, float(instance.amount)]
        instance.task.save()
        return resp


class NotificationViewSet(viewsets.ModelViewSet):
    """List of notifications to request user ordered by date."""

    serializer_class = NotificationSerializer
    permission_classes = ()

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(Q(recipient=user) | Q(recipient=None))
        return queryset.order_by('-created_at')


class DepositViewSet(viewsets.ModelViewSet):

    serializer_class = DepositSerializer
    permission_classes = (AuthenticatedPermissions,)

    def perform_create(self, serializer):
        serializer.save(
            recipient=self.request.user, title='deposit', types=TransactionType.DEPOSIT
        )


@method_decorator(name='list', decorator=loan_schema)
@method_decorator(name='retrieve', decorator=loan_schema)
@method_decorator(name='partial_update', decorator=loan_schema)
@method_decorator(name='create', decorator=loan_schema)
class LoanViewSet(viewsets.ModelViewSet):

    permission_classes = (
        AuthenticatedPermissions,
        ChildCreatePermissions,
        LoanObjectPermissions,
    )

    def get_queryset(self):
        user = self.request.user
        if user.user_type == UserType.PARENT:
            return Loan.objects.filter(lender=user)
        return Loan.objects.filter(borrower=user)

    def perform_create(self, serializer):
        serializer.save(borrower=self.request.user)

    def get_serializer_class(self):
        if self.request.user.user_type == UserType.PARENT:
            return LoanParentSerializer
        return LoanChildSerializer


class LoanPayoffViewSet(viewsets.ModelViewSet):

    serializer_class = LoanPayoffSerializer
    permission_classes = (AuthenticatedPermissions,)

    def perform_create(self, serializer):
        loan = get_object_or_404(Loan, id=self.kwargs['loan_id'])
        if self.request.user != loan.borrower:
            raise PermissionDenied({"message": "You don't have permission to access"})
        serializer.save(
            recipient=self.request.user,
            title='',
            types=TransactionType.LOAN,
            loan=loan,
        )


class WithdrawViewSet(viewsets.ModelViewSet):

    permission_classes = (AuthenticatedPermissions,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateWithdrawSerializer
        return WithdrawSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(sender=self.kwargs['user_id'], type=TransactionType.WITHDRAW)

    def perform_create(self, serializer):
        serializer.save(
            sender=self.request.user, title='Withdraw', types=TransactionType.WITHDRAW
        )
        print(serializer)

    def create(self, request, *args, **kwargs):
        user = CustomUser.objects.get(id=request.user.id)
        if user.balance < float(request.data['amount']):
            return Response(
                {"message": "Not enough funds on the account!"}, status.HTTP_400_BAD_REQUEST
            )

        limit_check, resp = period_limit_check(user)
        if limit_check:
            return resp

        if user.parental_control == ControlType.CONFIRMATION:
            resp = Response({"message": "Transaction must be accepted by parent."}, status.HTTP_201_CREATED)
            super().create(request, *args, **kwargs)
            return resp

        resp = super().create(request, *args, **kwargs)

        return resp
