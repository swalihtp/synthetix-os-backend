import django_filters

from .models import MeetingSummaryExecution, ResumeExecution


class ResumeExecutionFilter(django_filters.FilterSet):
    workflow_execution_id = django_filters.UUIDFilter(
        field_name="workflow_execution_id"
    )
    workflow_id = django_filters.UUIDFilter(
        field_name="workflow_execution__workflow_id"
    )
    agent_id = django_filters.UUIDFilter(
        field_name="workflow_execution__workflow__agent_id"
    )
    file_name = django_filters.CharFilter(field_name="file_name", lookup_expr="icontains")
    job_title = django_filters.CharFilter(field_name="job_title", lookup_expr="icontains")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    created_at_from = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_to = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    updated_at_from = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gte"
    )
    updated_at_to = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="lte"
    )

    class Meta:
        model = ResumeExecution
        fields = [
            "workflow_execution_id",
            "workflow_id",
            "agent_id",
            "file_name",
            "job_title",
            "status",
            "created_at_from",
            "created_at_to",
            "updated_at_from",
            "updated_at_to",
        ]


class MeetingSummaryExecutionFilter(django_filters.FilterSet):
    workflow_execution_id = django_filters.UUIDFilter(
        field_name="workflow_execution_id"
    )
    workflow_id = django_filters.UUIDFilter(
        field_name="workflow_execution__workflow_id"
    )
    agent_id = django_filters.UUIDFilter(
        field_name="workflow_execution__workflow__agent_id"
    )
    file_name = django_filters.CharFilter(field_name="file_name", lookup_expr="icontains")
    summary_style = django_filters.CharFilter(
        field_name="summary_style", lookup_expr="iexact"
    )
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    created_at_from = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_to = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    updated_at_from = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gte"
    )
    updated_at_to = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="lte"
    )

    class Meta:
        model = MeetingSummaryExecution
        fields = [
            "workflow_execution_id",
            "workflow_id",
            "agent_id",
            "file_name",
            "summary_style",
            "status",
            "created_at_from",
            "created_at_to",
            "updated_at_from",
            "updated_at_to",
        ]
