# 3rd-party
from rest_framework import permissions


class AuthenticatedPermissions(permissions.BasePermission):
    """Family members access."""

    def has_permission(self, request, view):
        """User accesses."""
        return request.user.is_authenticated
