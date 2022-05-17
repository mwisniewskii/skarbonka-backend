# Django
from django.db.models import Q
from django.utils.decorators import method_decorator

# 3rd-party
from django_fsm import can_proceed
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Project
from accounts.models import UserType
from accounts.permissions import ParentCUDPermissions

# Local
from .enum import TransactionType, LoanState
from .models import Allowance
from .models import Loan
from .models import Notification
from .models import Transaction
from .permissions import AuthenticatedPermissions
from .permissions import ChildCreatePermissions
from .permissions import FamilyAllowancesPermissions
from .permissions import LoanObjectPermissions
from .permissions import OwnObjectOrParentOfFamilyPermissions
from .permissions import ParentPatchPermissions
from .serializers import AllowanceSerializer
from .serializers import CreateWithdrawSerializer
from .serializers import DepositSerializer
from .serializers import LoanChildSerializer
from .serializers import LoanParentSerializer
from .serializers import LoanPayoffSerializer
from .serializers import NotificationSerializer
from .serializers import WithdrawSerializer
from .swagger_schemas import loan_schema


class TransactionCreateMixin:

    def create(self, request, *args, **kwargs):
        """Method require implemented method perform_create which returns transaction object."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)

        if can_proceed(obj.to_confirm):
            obj.to_confirm()
            obj.save()
            return Response(
                {"message": "Transaction must be accepted by parent."}, status.HTTP_202_ACCEPTED
            )

        if can_proceed(obj.accept):
            obj.accept()
            obj.save()
            return Response(
                {"message": "Not enough funds on the account!"}, status.HTTP_400_BAD_REQUEST
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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

    def perform_update(self, serializer):
        return serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['state'] = request.data.pop('state')
        if kwargs['state'] not in [LoanState.GRANTED, LoanState.DECLINED]:
            return Response({"message": "Invalid options, state must by Granted or Declined"},
                            status.HTTP_400_BAD_REQUEST)

        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        loan = self.perform_update(serializer)
        if kwargs['state'] == LoanState.GRANTED:
            if not can_proceed(loan.grant()):
                return Response({"message": "Not enough funds on the account!"}, status.HTTP_400_BAD_REQUEST)
            loan.grant()
        if kwargs['state'] == LoanState.DECLINED:
            if not can_proceed(loan.decline()):
                return Response({"message": "Only pending loans can be rejected."}, status.HTTP_400_BAD_REQUEST)
            loan.decline()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class LoanPayoffViewSet(viewsets.ModelViewSet, TransactionCreateMixin):

    serializer_class = LoanPayoffSerializer
    permission_classes = (AuthenticatedPermissions,)

    def perform_create(self, serializer):
        loan = get_object_or_404(Loan, id=self.kwargs['loan_id'])
        if self.request.user != loan.borrower:
            raise PermissionDenied({"message": "You don't have permission to access"})
        return serializer.save(
            recipient=self.request.user,
            title='Spłata pożyczki',
            types=TransactionType.LOAN,
            loan=loan,
        )


class WithdrawViewSet(viewsets.ModelViewSet, TransactionCreateMixin):

    permission_classes = (
        AuthenticatedPermissions,
        ParentPatchPermissions,
        OwnObjectOrParentOfFamilyPermissions,
    )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateWithdrawSerializer
        return WithdrawSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            sender=self.kwargs['user_id'], types=TransactionType.WITHDRAW
        )

    def perform_create(self, serializer):
        return serializer.save(sender=self.request.user, title='Withdraw', types=TransactionType.WITHDRAW)
