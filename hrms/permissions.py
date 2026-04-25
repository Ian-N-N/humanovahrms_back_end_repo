from rest_framework.permissions import BasePermission, SAFE_METHODS


def role_name(user):
    return getattr(getattr(user, "role", None), "name", None)


def is_admin(user):
    return bool(user and user.is_authenticated and role_name(user) == "Admin")


def is_hr(user):
    return bool(user and user.is_authenticated and role_name(user) in {"Admin", "HR Manager"})


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)


class IsHrRole(BasePermission):
    def has_permission(self, request, view):
        return is_hr(request.user)


class IsHrOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return is_hr(request.user)


class OwnNotification(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class EmployeeOwnerOrHr(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_hr(request.user):
            return True
        return getattr(obj, "user_id", None) == request.user.id


class PayrollOwnerOrHr(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_hr(request.user):
            return True
        return getattr(obj.employee, "user_id", None) == request.user.id


class LeaveOwnerOrHr(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_hr(request.user):
            return True
        return getattr(obj.employee, "user_id", None) == request.user.id
