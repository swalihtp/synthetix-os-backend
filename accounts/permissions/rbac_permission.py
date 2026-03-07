from rest_framework.permissions import BasePermission
from accounts.services.rbac_service import RBACService


class RBACPermission(BasePermission):

    def has_permission(self, request, view):
        required_permission = getattr(view, 'required_permission', None)

        # No permission required
        if not required_permission:
            return True

        return RBACService.has_permission(request.user, required_permission)

    def has_object_permission(self, request, view, obj):
        required_permission = getattr(view, 'required_permission', None)

        if not RBACService.has_permission(request.user, required_permission):
            return False

        # Ownership check
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return True