from rest_framework import permissions


class IsAdminOrHR(permissions.BasePermission):
    """Full access for Admin/HR roles only."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_or_hr)


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "ADMIN")


class ReadOnlyOrAdminHR(permissions.BasePermission):
    """Anyone authenticated can read; only Admin/HR can write."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_or_hr)


class IsOwnerOrAdminHR(permissions.BasePermission):
    """Object-level check: owner of the record, or Admin/HR."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_or_hr:
            return True
        owner_user = getattr(getattr(obj, "employee", obj), "user", None)
        return owner_user == request.user
