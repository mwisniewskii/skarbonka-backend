# 3rd-party
from rest_framework import permissions


class FamilyAllowancesPermissions(permissions.BasePermission):
    """Family members access."""

    def has_object_permission(self, request, view, obj):
        """Only family member access."""
        return obj.parent == request.user.family or request.user.is_superuser or obj.child == request.user.family

