# 3rd-party
from rest_framework import permissions

# Project
from accounts.models import UserType


class FamilyResourcesPermissions(permissions.BasePermission):
    """Family members access."""

    def has_object_permission(self, request, view, obj):
        """Only family member access."""
        return obj.family == request.user.family or request.user.is_superuser


class ParentCUDPermissions(permissions.BasePermission):
    """Parent creat, delete, update permissions."""

    def has_permission(self, request, view):
        """Parent accesses to create, modify and delete members."""
        if not request.user.is_authenticated:
            return False
        if request.method in ["POST", "DELETE", "PUT", "PATCH"]:
            return request.user.user_type == UserType.PARENT
        return True
