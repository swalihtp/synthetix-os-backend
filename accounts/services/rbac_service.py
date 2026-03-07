class RBACService:

    @staticmethod
    def has_permission(user, permission_code):
        if not user.is_authenticated or not user.role:
            return False

        if not hasattr(user, '_perm_cache'):
            user._perm_cache = set(
                user.role.permissions.values_list('code', flat=True)
            )

        return permission_code in user._perm_cache