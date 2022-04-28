# 3rd-party
from rest_framework import permissions

# Project
from accounts.models import UserType


class FamilyAllowancesPermissions(permissions.BasePermission):
    """Family members access."""

    def has_object_permission(self, request, view, obj):
        """Only family member access."""
        return (
            obj.parent.family == request.user.family
            or request.user.is_superuser
            or obj.child == request.user
        )


class LoanObjectPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.lender == request.user or obj.borrower == request.user or request.user.is_superuser
        )


class LoanObjectBorrowerPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.borrower == request.user or request.user.is_superuser


class AuthenticatedPermissions(permissions.BasePermission):
    """User authenticated."""

    def has_permission(self, request, view):
        return request.user.is_authenticated


class ChildCreatePermissions(permissions.BasePermission):
    """Child create permissions."""

    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.user_type == UserType.CHILD
        return True


class ParentPatchPermissions(permissions.BasePermission):
    """Parent patch permissions."""

    def has_permission(self, request, view):
        if request.method == "PATCH":
            return request.user.user_type == UserType.PARENT
        return True


class OwnObjectOrParentOfFamilyPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        parent = (
            request.user.family == obj.sender.family and request.user.user_type == UserType.PARENT
        )
        return obj.sender == request.user or parent
