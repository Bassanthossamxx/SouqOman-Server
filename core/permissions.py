from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions
class IsSuperUserOrReadOnly(BasePermission):
    """
    Allow GET/HEAD/OPTIONS to everyone,
    but only superusers can POST, PUT, PATCH, DELETE.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser

class IsOwnerOrSuperUser(permissions.BasePermission):
    """Allow owners or superusers to edit/delete"""
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj.user == request.user

class IsSuperUser(BasePermission):
    """Require authenticated superuser for all methods (no public read)."""
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_superuser)
