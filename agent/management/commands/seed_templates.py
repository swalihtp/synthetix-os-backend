from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from agent.models import Agent
from workflows.models import Workflow, WorkflowStep

User = get_user_model()


TEMPLATES = [
    {
        "agent": {
            "name": "Smart Email Agent",
            "description": "Reads incoming emails, classifies intent, and sends intelligent replies automatically.",
            "prompt": "When I receive an email, analyze it and reply appropriately.",
        },
        "workflow": {
            "name": "Auto Email Reply",
            "trigger_type": "gmail.email_received",
            "trigger_config": {"filter": "unread", "label": "INBOX"},
        },
        "steps": [
            {
                "step_type": "ai",
                "action": "gmail.fetch_email",
                "config": {},
                "order": 1,
                "on_failure": "stop",
            },
            {
                "step_type": "ai",
                "action": "ai.analyze_email",
                "config": {},
                "order": 2,
                "on_failure": "stop",
            },
            {
                "step_type": "ai",
                "action": "ai.classify_intent",
                "config": {
                    "detect": ["meeting_request", "complaint", "general", "urgent"]
                },
                "order": 3,
                "on_failure": "stop",
            },
            {
                "step_type": "ai",
                "action": "ai.generate_reply",
                "config": {"tone": "professional"},
                "order": 4,
                "on_failure": "stop",
            },
            {
                "step_type": "system",
                "action": "gmail.send_reply",
                "config": {},
                "order": 5,
                "on_failure": "stop",
            },
        ],
    },
    {
        "agent": {
            "name": "Meeting Scheduler",
            "description": "Detects meeting requests in emails, checks calendar availability, and books meetings automatically.",
            "prompt": "When someone emails asking for a meeting, check my calendar and schedule it.",
        },
        "workflow": {
            "name": "Auto Meeting Booking",
            "trigger_type": "gmail.email_received",
            "trigger_config": {"filter": "unread"},
        },
        "steps": [
            {
                "step_type": "ai",
                "action": "gmail.fetch_email",
                "config": {},
                "order": 1,
                "on_failure": "stop",
            },
            {
                "step_type": "ai",
                "action": "ai.detect_meeting_intent",
                "config": {},
                "order": 2,
                "on_failure": "stop",
            },
            {
                "step_type": "system",
                "action": "calendar.check_availability",
                "config": {"days_ahead": 7},
                "order": 3,
                "on_failure": "stop",
            },
            {
                "step_type": "system",
                "action": "calendar.create_event",
                "config": {"duration_minutes": 30},
                "order": 4,
                "on_failure": "stop",
            },
            {
                "step_type": "ai",
                "action": "ai.generate_reply",
                "config": {"tone": "friendly"},
                "order": 5,
                "on_failure": "stop",
            },
            {
                "step_type": "system",
                "action": "gmail.send_reply",
                "config": {},
                "order": 6,
                "on_failure": "stop",
            },
        ],
    },
    {
        "agent": {
            "name": "Social Post Scheduler",
            "description": "Takes your content idea and automatically adapts and schedules it across Twitter, LinkedIn, and Instagram.",
            "prompt": "Take my content and post it across all my social media platforms.",
        },
        "workflow": {
            "name": "Multi-Platform Social Post",
            "trigger_type": "api.trigger",
            "trigger_config": {"endpoint": "social-scheduler"},
        },
        "steps": [
            {
                "step_type": "ai",
                "action": "ai.extract_content",
                "config": {},
                "order": 1,
                "on_failure": "stop",
            },
            {
                "step_type": "ai",
                "action": "ai.adapt_twitter",
                "config": {"platform": "twitter", "max_chars": 280},
                "order": 2,
                "on_failure": "continue",
            },
            {
                "step_type": "ai",
                "action": "ai.adapt_linkedin",
                "config": {"platform": "linkedin", "tone": "professional"},
                "order": 3,
                "on_failure": "continue",
            },
            {
                "step_type": "ai",
                "action": "ai.adapt_instagram",
                "config": {"platform": "instagram", "caption_style": True},
                "order": 4,
                "on_failure": "continue",
            },
            {
                "step_type": "system",
                "action": "system.schedule_posts",
                "config": {
                    "platforms": ["twitter", "linkedin", "instagram"]
                },
                "order": 5,
                "on_failure": "stop",
            },
            {
                "step_type": "system",
                "action": "system.notify_user",
                "config": {
                    "channel": "telegram",
                    "message": "Your posts have been scheduled across all platforms!"
                },
                "order": 6,
                "on_failure": "continue",
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed database with pre-built workflow templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='User email to assign templates to',
            required=True,
        )

    def handle(self, *args, **options):
        email = options['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {email} not found.')
            )
            return

        created_count = 0

        for template in TEMPLATES:
            # Skip if agent already exists for this user
            if Agent.objects.filter(
                user=user,
                name=template['agent']['name']
            ).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping '{template['agent']['name']}' — already exists."
                    )
                )
                continue

            # Create agent
            agent = Agent.objects.create(
                user=user,
                **template['agent']
            )

            # Create workflow
            workflow = Workflow.objects.create(
                agent=agent,
                **template['workflow']
            )

            # Create steps
            for step_data in template['steps']:
                WorkflowStep.objects.create(
                    workflow=workflow,
                    **step_data
                )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created: {template['agent']['name']}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. {created_count} templates created for {email}.'
            )
        )           