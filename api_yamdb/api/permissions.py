from rest_framework import permissions
from reviews.models import ADMIN

NOT_YOUR_CONTENT = 'У вас недостаточно прав для выполнения данного действия.'


class AuthorOrHigher(permissions.BasePermission):
    """Предоставление доступа автору, модератору, админу."""

    message = NOT_YOUR_CONTENT

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
            or request.user.is_superuser
        )


class AdminOrReadOnly(permissions.BasePermission):
    """Предоставление доступа админу."""

    message = NOT_YOUR_CONTENT

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated and (
            request.user.role == ADMIN
            or request.user.is_staff
            or request.user.is_superuser
        ):
            return True
        return False


class AdminOnly(permissions.BasePermission):
    """Только для администраторов"""

    def has_permission(self, request, view):
        if request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_staff
            or request.user.is_superuser
        ):
            return True
        return False
