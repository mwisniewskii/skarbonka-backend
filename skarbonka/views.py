# Standard Library
from decimal import Decimal
from re import S

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
from django_filters.rest_framework import DjangoFilterBackend
# Project
from accounts.models import CustomUser
from accounts.models import UserType
from accounts.permissions import ParentCUDPermissions

# Local
from .enum import LoanState
from .enum import TransactionState
from .models import Allowance
from .models import Loan
from .models import Notification
from .models import Transaction
from .models import TransactionType
from .permissions import AuthenticatedPermissions
from .permissions import ChildCreatePermissions
from .permissions import FamilyAllowancesPermissions
from .permissions import FamilyTransacionPermissions
from .permissions import LoanObjectPermissions
from .permissions import OwnObjectOrParentOfFamilyPermissions
from .permissions import ParentPatchPermissions
from .permissions import HistoryPermissions
from .serializers import AllowanceSerializer, HistoryFilter
from .serializers import CreateWithdrawSerializer
from .serializers import DepositSerializer
from .serializers import LoanChildSerializer
from .serializers import LoanParentSerializer
from .serializers import LoanPayoffSerializer
from .serializers import NotificationSerializer
from .serializers import TransactionDetailSerializer
from .serializers import TransactionSerializer
from .serializers import WithdrawSerializer
from .serializers import HistorySerializer
from .serializers import HistoryFilter
from .swagger_schemas import loan_schema
from .swagger_schemas import withdraw_post_schema


class TransactionCreateMixin:
    def create(self, request, *args, **kwargs):
        """Method require implemented method perform_create which returns transaction object."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        if not can_proceed(obj.accept):
            obj.fail()
            obj.save()
            return Response(
                {"message": "Not enough funds on the account!"}, status.HTTP_400_BAD_REQUEST
            )
        if can_proceed(obj.to_confirm):
            obj.to_confirm()
            obj.save()
            return Response(
                {"message": "Transaction must be accepted by parent."}, status.HTTP_202_ACCEPTED
            )
        obj.accept()
        obj.save()
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


class TransactionViewSet(TransactionCreateMixin, viewsets.ModelViewSet):

    serializer_class = TransactionSerializer
    permission_classes = (FamilyTransacionPermissions,)

    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(Q(sender=user))
        return queryset

    def perform_create(self, serializer, *args, **kwargs):
        return serializer.save(
            sender=self.request.user,
            types=TransactionType.ORDINARY,
        )

    def create(self, request, *args, **kwargs):
        user = CustomUser.objects.get(id=request.user.id)
        recipient = CustomUser.objects.get(id=request.data['recipient'])
        if not user.family == recipient.family:
            return Response({"message": "not a family member"}, status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)


class TransactionUpdateView(viewsets.ModelViewSet):
    serializer_class = TransactionDetailSerializer
    permission_classes = (ParentPatchPermissions,)

    def dispatch(self, request, *args, **kwargs):
        resp = super().dispatch(request, *args, **kwargs)
        obj = self.get_object()
        if (
            self.request.user.family != obj.sender.family
            or self.request.user.family != obj.recipient.family
        ):
            return Response(
                {"message": "This resource does not belong to your family!"},
                status.HTTP_403_FORBIDDEN,
            )
        return resp

    def perform_update(self, serializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        transaction = self.perform_update(serializer)

        if kwargs['state'] == TransactionState.ACCEPTED:
            if not can_proceed(transaction.accept()):
                return Response(
                    {"message": "Not enough funds on the account!"}, status.HTTP_400_BAD_REQUEST
                )
            transaction.grant()
        if kwargs['state'] == TransactionState.DECLINED:
            if not can_proceed(transaction.decline()):
                return Response(
                    {"message": "Only pending loans can be rejected."}, status.HTTP_400_BAD_REQUEST
                )
            transaction.decline()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class DepositViewSet(viewsets.ModelViewSet):

    serializer_class = DepositSerializer
    permission_classes = (AuthenticatedPermissions,)

    def perform_create(self, serializer):
        return serializer.save(
            recipient=self.request.user, title='deposit', types=TransactionType.DEPOSIT
        )

    def create(self, request, *args, **kwargs):
        """Method require implemented method perform_create which returns transaction object."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        if can_proceed(obj.accept):
            obj.accept()
            obj.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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

    def get_serializer_class(self):
        if self.request.user.user_type == UserType.PARENT:
            return LoanParentSerializer
        return LoanChildSerializer

    def perform_create(self, serializer):
        serializer.save(borrower=self.request.user)

    def create(self, request, *args, **kwargs):
        lender = CustomUser.objects.get(id=request.data["lender"])
        if lender.family != request.user.family:
            return Response(
                {"message": "The lender you choose does not belong to your family!"},
                status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def perform_update(self, serializer):
        return serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['loan_state'] = request.data.pop('loan_state')
        if kwargs['loan_state'] not in [LoanState.GRANTED, LoanState.DECLINED]:
            return Response(
                {"message": "Invalid options, the state can only be set to Granted or Declined"},
                status.HTTP_406_NOT_ACCEPTABLE,
            )

        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        loan = self.perform_update(serializer)

        match kwargs['loan_state']:
            case LoanState.GRANTED:
                if not can_proceed(loan.grant):
                    return Response(
                        {"message": "Not enough funds on the account!"},
                        status.HTTP_402_PAYMENT_REQUIRED,
                    )
                loan.grant()
                loan.save()
            case LoanState.DECLINED:
                if not can_proceed(loan.decline):
                    return Response(
                        {"message": "Only pending loans can be declined."},
                        status.HTTP_400_BAD_REQUEST,
                    )
                loan.decline()
                loan.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class LoanPayoffViewSet(TransactionCreateMixin, viewsets.ModelViewSet):

    serializer_class = LoanPayoffSerializer
    permission_classes = (AuthenticatedPermissions,)

    def dispatch(self, request, *args, **kwargs):
        self.loan = get_object_or_404(Loan, id=kwargs['loan_id'])
        return super().dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        if self.request.user != self.loan.borrower:
            raise PermissionDenied({"message": "You don't have permission to access"})
        return serializer.save(
            recipient=self.request.user,
            title='Spłata pożyczki',
            types=TransactionType.LOAN,
            loan=self.loan,
        )

    def create(self, request, *args, **kwargs):
        if self.loan.loan_state == LoanState.PAID:
            return Response({"message": f"This loan is repaid!"}, status.HTTP_400_BAD_REQUEST)
        if Decimal(request.data["amount"]) > self.loan.amount:
            return Response(
                {"message": f"You only have to pay back {self.loan.amount}"},
                status.HTTP_400_BAD_REQUEST,
            )
        resp = super().create(request, *args, **kwargs)
        if can_proceed(self.loan.pay_off):
            self.loan.pay_off()
            self.loan.save()
            self.loan.notify.delete()
        return Response(resp.data, status.HTTP_200_OK)


@method_decorator(name='create', decorator=withdraw_post_schema)
class WithdrawViewSet(TransactionCreateMixin, viewsets.ModelViewSet):

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
        return serializer.save(
            sender=self.request.user, title='Withdraw', types=TransactionType.WITHDRAW
        )

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
            resp = Response(
                {"message": "Transaction must be accepted by parent."}, status.HTTP_201_CREATED
            )
            super().create(request, *args, **kwargs)
            return resp

        resp = super().create(request, *args, **kwargs)

        return resp

class HistoryViewset(viewsets.ModelViewSet):

    serializer_class = HistorySerializer
    permission_classes = (AuthenticatedPermissions, HistoryPermissions,)
    filterset_class = HistoryFilter
    filter_backends = [
        DjangoFilterBackend,
    ]

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(sender=self.kwargs['user_id']) | Q(recipient=self.kwargs['user_id'])
        )
        
