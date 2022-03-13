from rest_framework import permissions


class HeadOfFamily(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in ['POST', 'DELETE', 'PUT']:
            return request.user.user_type == 1
        return True

    def has_object_permission(self, request, view, obj):
        return obj.family == request.user.family or request.user.is_superuser
