from rest_framework import permissions

class HasUserManagementPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Permitir acceso a cualquier usuario autenticado con un grupo
        return request.user.is_authenticated and request.user.groups.exists()