# 3rd-party
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

# Local
from .models import CustomUser
from .permissions import FamilyResourcesPermissions
from .permissions import ParentCUDPermissions
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Family members resources."""

    serializer_class = UserSerializer
    permission_classes = (FamilyResourcesPermissions, ParentCUDPermissions)

    def get_queryset(self):  # noqa: D102
        user = self.request.user
        if user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(family=user.family)

    def get_object(self):  # noqa: D102
        obj = get_object_or_404(CustomUser.objects.filter(id=self.kwargs["pk"]))
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):  # noqa: D102
        serializer.save(family=self.request.user.family)
