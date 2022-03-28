from rest_framework import viewsets

from accounts.permissions import FamilyMemberPermissions
from .models import Allowance
from .serializers import AllowanceSerializer
from accounts.models import UserType


class AllowanceViewSet(viewsets.ModelViewSet):
    """Family members resources."""

    serializer_class = AllowanceSerializer
    # permission_classes = (FamilyMemberPermissions,)

    def get_queryset(self):
        user = self.request.user
        if user.user_type == UserType.PARENT:
            return Allowance.objects.filter(parent=user)
        return Allowance.objects.filter(child=user)

    def perform_create(self, serializer):  # noqa: D102
        serializer.save(parent=self.request.user)
