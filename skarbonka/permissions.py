# 3rd-party
from rest_framework import permissions

# Project
from accounts.models import UserType
from skarbonka.enum import TransactionType


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
    """Permission to object of Loan."""

    def has_object_permission(self, request, view, obj):
        return (
            obj.lender == request.user or obj.borrower == request.user or request.user.is_superuser
        )


class LoanObjectBorrowerPermissions(permissions.BasePermission):
    """Checking whether the user is a borrower."""

    def has_object_permission(self, request, view, obj):
        return obj.borrower == request.user or request.user.is_superuser


class AuthenticatedPermissions(permissions.BasePermission):
    """Checking if the user is authorized."""

    def has_permission(self, request, view):
        return request.user.is_authenticated


class ChildCreatePermissions(permissions.BasePermission):
    """Child Post method permissions."""

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
    """Permission for object owner or parent of owner."""

    def has_object_permission(self, request, view, obj):
        parent = (
            request.user.family == obj.sender.family and request.user.user_type == UserType.PARENT
        )
        return obj.sender == request.user or parent


class FamilyTransacionPermissions(permissions.BasePermission):
    """Family members access."""

    def has_object_permission(self, request, view, obj):
        """Only family member access."""
        return (
            obj.sender == request.user.family
            or request.user.is_superuser
            or obj.recipient == request.user.family
        )
