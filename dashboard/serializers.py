from rest_framework import serializers


class OverviewSerializer(serializers.Serializer):
    agents = serializers.IntegerField()
    built_in_agents = serializers.IntegerField()
    workflows = serializers.IntegerField()
    running_workflows = serializers.IntegerField()
    completed_today = serializers.IntegerField()
    failed_today = serializers.IntegerField()


class TodayActivitySerializer(serializers.Serializer):
    ai_calls = serializers.IntegerField()
    email_processed = serializers.IntegerField()
    resumes_analyzed = serializers.IntegerField()
    meetings_summarized = serializers.IntegerField()


class ContinueWorkingSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.CharField()
    title = serializers.CharField()
    status = serializers.CharField()
    updated_at = serializers.DateTimeField()


class RecentActivitySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.CharField()
    title = serializers.CharField()
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()


class ApplicationSerializer(serializers.Serializer):
    name = serializers.CharField()
    total_runs = serializers.IntegerField()


class WorkflowStatisticsSerializer(serializers.Serializer):
    completed = serializers.IntegerField()
    running = serializers.IntegerField()
    failed = serializers.IntegerField()


class DashboardSerializer(serializers.Serializer):
    overview = OverviewSerializer()
    today_activity = TodayActivitySerializer()
    continue_working = ContinueWorkingSerializer(many=True)
    recent_activity = RecentActivitySerializer(many=True)
    applications = ApplicationSerializer(many=True)
    workflow_statistics = WorkflowStatisticsSerializer()
