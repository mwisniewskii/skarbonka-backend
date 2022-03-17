# 3rd-party
from rest_framework import permissions


class FamilyMemberPermissions(permissions.BasePermission):
    """Family members access."""

    def has_permission(self, request, view):
        """Parent accesses to create, modify and delete members."""
        if not request.user.is_authenticated:
            return False
        if request.method in ["POST", "DELETE", "PUT"]:
            return request.user.user_type == 1
        return True

    def has_object_permission(self, request, view, obj):
        """Only family member access."""
        return obj.family == request.user.family or request.user.is_superuser
