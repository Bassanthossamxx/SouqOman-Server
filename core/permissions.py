from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSuperUserOrReadOnly(BasePermission):
    """
    Allow GET/HEAD/OPTIONS to everyone,
    but only superusers can POST, PUT, PATCH, DELETE.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser
