from rest_framework.permissions import BasePermission

from .models import User


class IsExecutiveOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.Role.EXECUTIVE, User.Role.ADMIN]


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN
