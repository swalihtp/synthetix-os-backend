import django_filters
from accounts.models import User
from agent.models import BuiltInAgent

class UserRegistryFilter(django_filters.FilterSet):
    role        = django_filters.CharFilter(field_name='role__name', lookup_expr='iexact')
    is_active   = django_filters.BooleanFilter(field_name='is_active')
    created_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_to  = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = User
        fields = ['role', 'is_active', 'created_from', 'created_to']
        
class BuiltInAgentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    has_tools = django_filters.BooleanFilter(method='filter_has_tools')
    has_integrations = django_filters.BooleanFilter(method='filter_has_integrations')

    class Meta:
        model = BuiltInAgent
        fields = ['name']

    def filter_has_tools(self, queryset, name, value):
        return queryset.exclude(tools__isnull=True) if value else queryset.filter(tools__isnull=True)

    def filter_has_integrations(self, queryset, name, value):
        return (
            queryset.exclude(required_integrations__isnull=True)
            if value
            else queryset.filter(required_integrations__isnull=True)
        )