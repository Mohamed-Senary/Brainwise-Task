from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth import get_user_model

User = get_user_model()

class IsAdmin(BasePermission):
    def has_permission(self,request,view):
        return request.user.is_authenticated and request.user.role == User.Roles.ADMIN

class IsHR(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Roles.HR


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Roles.MANAGER


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Roles.EMPLOYEE
