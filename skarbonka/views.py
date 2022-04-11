# Django
from django.db.models import Q

# 3rd-party
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status

# Project
from accounts.models import UserType
from accounts.permissions import ParentCUDPermissions

# Local
from .models import Allowance
from .models import Loan
from .models import Notification
from .permissions import AuthenticatedPermissions
from .permissions import ChildCreatePermissions
from .permissions import FamilyAllowancesPermissions
from .permissions import LoanObjectPermissions
from .serializers import AllowanceSerializer, LoanSampleSerializer
from .serializers import LoanChildSerializer
from .serializers import LoanParentSerializer
from .serializers import NotificationSerializer
from .swagger_schemas import loan_schema


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

    serializer_class = NotificationSerializer
    permission_classes = ()

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(Q(recipient=user) | Q(recipient=None))
        return queryset.order_by('-created_at')


@method_decorator(name='list', decorator=loan_schema)
@method_decorator(name='retrieve', decorator=loan_schema)
@method_decorator(name='partial_update', decorator=loan_schema)
class LoanViewSet(viewsets.ModelViewSet):

    permission_classes = (AuthenticatedPermissions, ChildCreatePermissions, LoanObjectPermissions)

    def get_queryset(self):
        user = self.request.user
        if user.user_type == UserType.PARENT:
            return Loan.objects.filter(lender=user)
        return Loan.objects.filter(borrower=user)

    def perform_create(self, serializer):
        serializer.save(borrower=self.request.user)

    @loan_schema
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.user.user_type == UserType.PARENT:
            return LoanParentSerializer
        return LoanChildSerializer

    def update(self, request, *args, **kwargs):
        """Set payment date and status."""
        resp = super().update(request, *args, **kwargs)

        return resp
