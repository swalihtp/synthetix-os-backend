from itertools import chain
from operator import attrgetter

from agent.serializers import BuiltInAgentSerializer

from . import selectors


class DashboardService:

    def __init__(self, user):

        self.user = user

        self.resume = selectors.get_recent_resume_executions(user)

        self.meeting = selectors.get_recent_meeting_executions(user)

        self.email = selectors.get_recent_email_executions(user)

    def get_dashboard(self):
        return {
            "overview": self._get_overview(),
            "today_activity": self._get_today_activity(),
            "continue_working": self._get_continue_working(),
            "recent_activity": self._get_recent_activity(),
            "applications": self._get_applications(),
            "workflow_statistics": self._get_workflow_statistics(),
            "recommendations": self._get_recommendations(),
        }

    def _get_overview(self):
        return {
            "agents": selectors.get_agent_count(self.user),
            "built_in_agents": selectors.get_builtin_agent_count(),
            "workflows": selectors.get_workflow_count(self.user),
            "running_workflows": selectors.get_running_workflow_count(self.user),
            "completed_today": selectors.get_completed_today(self.user),
            "failed_today": selectors.get_failed_today(self.user),
        }

    def _get_today_activity(self):
        return {
            "ai_calls": selectors.get_ai_calls_today(self.user),
            "email_processed": selectors.get_email_processed_today(self.user),
            "resumes_analyzed": selectors.get_resume_analysis_today(self.user),
            "meetings_summarized": selectors.get_meeting_summary_today(self.user),
        }

    def _get_applications(self):

        usage = selectors.get_application_usage(self.user)

        return [
            {
                "name": name,
                "total_runs": total,
            }
            for name, total in usage.items()
        ]

    def _get_workflow_statistics(self):

        stats = selectors.get_workflow_status_summary(self.user)

        return {
            "completed": stats["SUCCESS"],
            "failed": stats["FAILED"],
            "running": stats["RUNNING"],
            "pending": stats["PENDING"],
        }

    def _get_recommendations(self):

        queryset = selectors.get_builtin_agents()

        return BuiltInAgentSerializer(queryset, many=True).data

    def _get_continue_working(self):

        resume = [
            {
                "id": r.id,
                "type": "resume",
                "title": r.file_name,
                "status": r.status,
                "updated_at": r.updated_at,
            }
            for r in selectors.get_recent_resume_executions(self.user, 3)
        ]

        meeting = [
            {
                "id": m.id,
                "type": "meeting",
                "title": m.file_name,
                "status": m.status,
                "updated_at": m.updated_at,
            }
            for m in selectors.get_recent_meeting_executions(self.user, 3)
        ]

        email = [
            {
                "id": e.id,
                "type": "email",
                "title": e.original_subject,
                "status": e.result,
                "updated_at": e.processed_at,
            }
            for e in selectors.get_recent_email_executions(self.user, 3)
        ]

        items = resume + meeting + email

        items.sort(
            key=lambda x: x["updated_at"],
            reverse=True,
        )

        return items[:8]

    def _get_recent_activity(self):

        activity = []

        for r in selectors.get_recent_resume_executions(self.user, 5):

            activity.append(
                {
                    "id": r.id,
                    "type": "resume",
                    "title": r.file_name,
                    "status": r.status,
                    "timestamp": r.updated_at,
                }
            )

        for m in selectors.get_recent_meeting_executions(self.user, 5):

            activity.append(
                {
                    "id": m.id,
                    "type": "meeting",
                    "title": m.file_name,
                    "status": m.status,
                    "timestamp": m.updated_at,
                }
            )

        for e in selectors.get_recent_email_executions(self.user, 5):

            activity.append(
                {
                    "id": e.id,
                    "type": "email",
                    "title": e.original_subject,
                    "status": e.result,
                    "timestamp": e.processed_at,
                }
            )

        activity.sort(
            key=lambda x: x["timestamp"],
            reverse=True,
        )

        return activity[:10]
