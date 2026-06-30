from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class AdminUserRegistryThrottle(UserRateThrottle):
    rate = '100/hour'
    scope = 'admin_user_registry'
    
class AdminBuiltInAgentThrottle(UserRateThrottle):
    """Scope rate is configured in settings.DEFAULT_THROTTLE_RATES."""
    scope = 'admin_builtin_agent'