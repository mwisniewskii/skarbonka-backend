# 3rd-party
from rest_framework import permissions


class UserPermitions(permissions.BasePermission):
    """Family members access."""

    def has_permission(self, request, view):
        """User accesses."""
        return request.user.is_authenticated
