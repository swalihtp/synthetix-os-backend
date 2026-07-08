from rest_framework import serializers


class UserStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    active = serializers.IntegerField()


class AgentStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()


class WorkflowExecutionStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    success = serializers.IntegerField()
    failed = serializers.IntegerField()
    running = serializers.IntegerField()


class DashboardStatisticsSerializer(serializers.Serializer):
    users = UserStatisticsSerializer()
    agents = AgentStatisticsSerializer()
    workflow_executions = WorkflowExecutionStatisticsSerializer()
