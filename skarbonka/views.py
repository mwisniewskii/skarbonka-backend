# Django
from difflib import restore
from typing_extensions import Self
from django.db.models import Q
from requests import request
import accounts

# 3rd-party
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

# Project
from accounts.models import CustomUser, UserType
from accounts.permissions import ParentCUDPermissions

# Local
from .models import Allowance, TransactionType
from .models import Notification
from .models import Transaction
from .permissions import FamilyAllowancesPermissions
from .permissions import FamilyTransacionPermissions
from .serializers import AllowanceSerializer, TransactionSerializer
from .serializers import NotificationSerializer


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


class TransactionViewSet(viewsets.ModelViewSet):

    serializer_class = TransactionSerializer
    permission_classes = (FamilyTransacionPermissions,)

    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(Q(sender=user))
        return queryset

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(
            sender=self.request.user,
            types=TransactionType.ORDINARY,
        )

    def create(self, request, *args, **kwargs):
        user = CustomUser.objects.get(id=request.user.id)
        recipient = CustomUser.objects.get(id=request.data['recipient'])
        if user.family == recipient.family:
            resp = super().create(request, *args, **kwargs)
            return resp
        resp = Response({"message": "not a family member"}, status.HTTP_400_BAD_REQUEST)
        return resp
