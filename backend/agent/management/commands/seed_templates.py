from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from agent.models import BuiltInAgent

User = get_user_model()


TEMPLATES = [
    {
        "agent": {
            "name": "Smart Email Agent",
            "type": "communication_agent",
            "description": "Autonomously reads emails, understands intent, retrieves context, and generates intelligent replies.",
            "objective": "Process incoming emails, understand user intent, retrieve relevant past conversations, and generate context-aware professional replies.",
            "prompt": "You are an AI Email Assistant. Analyze incoming emails, understand intent, retrieve relevant past context, and generate professional and accurate replies.",
            "capabilities": [
                "email_parsing",
                "intent_detection",
                "context_retrieval",
                "llm_reasoning",
                "reply_generation",
                "email_sending",
                "memory_storage",
            ],
            "domain": ["email_automation", "customer_support", "meeting_coordination"],
        },
        "tools": ["llm"],
        "required_inputs": [
            {
                "name": "ai_reply_categories",
                "label": "What kind of emails should AI reply to?",
                "type": "multi_select",
                "required": True,
                "options": [
                    "Customer Support",
                    "Meeting Requests",
                    "Product Questions",
                    "Sales Inquiries",
                    "Follow Ups",
                    "Partnership Requests",
                    "Bug Reports",
                    "General Questions",
                ],
            },
            {
                "name": "human_review_categories",
                "label": "What kind of emails should be sent for human review?",
                "type": "multi_select",
                "required": True,
                "options": [
                    "Legal Issues",
                    "Refund Requests",
                    "Payment Disputes",
                    "Angry Customers",
                    "Enterprise Deals",
                    "Security Concerns",
                    "Hiring Requests",
                    "High Priority Clients",
                ],
            },
            {
                "name": "reference_documents",
                "label": "Documents AI should use while replying",
                "type": "file_upload",
                "required": False,
                "multiple": True,
                "max_files": 3,
                "accepted_formats": [".pdf", ".docx", ".txt", ".md"],
            },
            {
                "name": "ignore_rules",
                "label": "What kind of emails should AI ignore?",
                "type": "multi_select",
                "required": False,
                "options": [
                    "Spam",
                    "Newsletters",
                    "Promotions",
                    "Cold Outreach",
                    "Social Notifications",
                    "Automated Alerts",
                ],
            },
        ],
        "required_integrations": [{"name": "gmail", "label": "Gmail"}],
        "config": {
            "trigger": {
                "type": "gmail.email_received",
                "filters": {"exclude_self": True, "ignore_spam": True},
                "pipeline": {
                    "stages": [
                        {
                            "name": "ingestion",
                            "tasks": [
                                "gmail.fetch_email",
                                "gmail.parse_email",
                            ],
                        },
                        {
                            "name": "reasoning_intent",
                            "tasks": ["ai.detect_intent"],
                        },
                        {
                            "name": "memory",
                            "tasks": [
                                "rag.retrieve",
                            ],
                        },
                        {"name": "reasoning_context", "tasks": ["ai.analyze_context"]},
                        {
                            "name": "response",
                            "tasks": [
                                "ai.generate_reply",
                            ],
                        },
                        {
                            "name": "action",
                            "tasks": ["gmail.send_email"],
                        },
                        {
                            "name": "memory_store",
                            "tasks": [
                                "rag.store",
                            ],
                        },
                    ]
                },
            }
        },
        "memory": {
            "enabled": True,
            "type": "hybrid",
            "stores": {
                "short_term": "redis",
                "long_term": "postgres",
                "semantic": "pgvector",
            },
            "retention_policy": {"raw_data_days": 30, "embeddings_days": 365},
        },
        "ai_config": {
            "model": "gemini-1.5-pro",
            "temperature": 0.4,
            "tone": "professional",
            "output_style": "email_reply",
            "analysis_depth": "medium",
        },
        "actions": {"send_reply": True, "store_in_rag": True},
        "observability": {
            "logging": True,
            "trace_pipeline": True,
            "store_runs": True,
            "metrics": [
                "execution_time",
                "emails_processed",
                "reply_generated",
                "llm_cost",
            ],
        },
        "error_handling": {
            "retry_policy": {"max_retries": 2, "backoff": "exponential"},
            "fallback_mode": "draft_only",
        },
    },
    {
        "agent": {
            "name": "Market Intelligence Agent",
            "type": "research_agent",
            "description": "Researches a company, its competitors, and industry trends to generate market intelligence reports.",
            "objective": "Generate a comprehensive market intelligence report using company information, uploaded documents, competitor research, and industry trend analysis.",
            "prompt": "You are a Market Intelligence Agent. Analyze the provided company information, uploaded documents, competitor landscape, and industry trends. Generate actionable business insights, SWOT analysis, and strategic recommendations.",
            "capabilities": [
                "document_analysis",
                "web_research",
                "competitor_discovery",
                "trend_analysis",
                "swot_generation",
                "report_generation",
            ],
        },
        "workflow_configuration": {"trigger": {"type": "scheduled"}},
        "config": {},
        "required_integrations": [],
        "required_inputs": [
            {
                "name": "company_name",
                "label": "Company Name",
                "type": "text",
                "required": True,
                "min_length": 2,
                "max_length": 100,
                "placeholder": "e.g. OpenAI",
                "help_text": "Official company name",
            },
            {
                "name": "company_description",
                "label": "Company Description",
                "type": "textarea",
                "required": True,
                "min_length": 50,
                "max_length": 5000,
                "placeholder": "Describe company products, services, customers and business model.",
                "help_text": "More details produce better market intelligence reports.",
            },
            {
                "name": "industry",
                "label": "Industry",
                "type": "text",
                "required": True,
                "min_length": 2,
                "max_length": 100,
                "placeholder": "e.g. SaaS, Healthcare, FinTech",
            },
            {
                "name": "company_website",
                "label": "Company Website",
                "type": "url",
                "required": False,
                "placeholder": "https://company.com",
                "help_text": "Provide the official website URL.",
            },
            {
                "name": "competitors",
                "label": "Known Competitors",
                "type": "dynamic_url_list",
                "required": False,
                "max_items": 20,
                "placeholder": "https://competitor.com",
                "help_text": "Provide competitor websites. Official domains only.",
            },
            {
                "name": "reference_documents",
                "label": "Reference Documents",
                "type": "file_upload",
                "required": False,
                "multiple": True,
                "max_files": 3,
                "max_file_size_mb": 25,
                "accepted_formats": [".pdf", ".docx", ".txt"],
                "warning": "Avoid scanned PDFs. OCR quality may reduce report accuracy.",
            },
        ],
        "tools": ["tavily_search", "firecrawl_scraper", "llm"],
        "output": {
            "format": "markdown",
            "sections": [
                "executive_summary",
                "company_overview",
                "products_and_services",
                "competitor_analysis",
                "industry_trends",
                "swot_analysis",
                "recommendations",
                "sources",
            ],
        },
    },
    {
        "agent": {
            "name": "Resume Analyzer",
            "type": "career_agent",
            "description": "Analyzes resumes and provides structured feedback to improve quality, clarity, and ATS performance.",
            "objective": "Help users improve resumes using AI-driven evaluation and industry best practices.",
            "prompt": "You are an expert resume reviewer and career coach. Evaluate resumes, identify weaknesses, missing skills, formatting issues, ATS problems, and provide structured improvement suggestions.",
            "capabilities": [
                "resume_parsing",
                "ats_analysis",
                "skill_extraction",
                "gap_detection",
                "resume_scoring",
                "feedback_generation",
                "execution_history",
            ],
            "domain": ["career", "resume_review"],
        },
        "tools": ["llm"],
        "config": {
            "trigger": {
                "type": "manual_execution",
                "pipeline": [
                    {"name": "ingestion", "tasks": ["file.extract_text"]},
                    {
                        "name": "analysis",
                        "tasks": [
                            "ai.resume_analysis",
                            "ai.skill_evaluation",
                            "ai.ats_scoring",
                        ],
                    },
                    {"name": "output", "tasks": ["ai.generate_feedback_report"]},
                ],
            }
        },
        "memory": {
            "enabled": True,
            "type": "execution_history",
            "stores": {"long_term": "postgres"},
        },
        "ai_config": {
            "model": "gemini-1.5-pro",
            "temperature": 0.3,
            "output_style": "structured_report",
        },
        "actions": {"store_analysis": True},
    },
    {
        "agent": {
            "name": "Meeting Notes Generator",
            "type": "productivity_agent",
            "description": "Converts meeting transcripts into structured summaries with key points, decisions, and action items.",
            "objective": "Generate clean, structured meeting summaries from raw transcripts.",
            "prompt": "You are a professional meeting assistant. Convert transcripts into structured summaries including key discussion points, decisions, blockers, and action items.",
            "capabilities": [
                "transcript_parsing",
                "summarization",
                "decision_extraction",
                "action_item_extraction",
                "meeting_structure_generation",
                "execution_history",
            ],
            "domain": ["meetings", "productivity"],
        },
        "tools": ["llm"],
        "config": {
            "trigger": {
                "type": "manual_execution",
                "pipeline": [
                    {"name": "ingestion", "tasks": ["file.extract_text"]},
                    {
                        "name": "analysis",
                        "tasks": [
                            "ai.topic_detection",
                            "ai.decision_extraction",
                            "ai.action_item_extraction",
                        ],
                    },
                    {"name": "output", "tasks": ["ai.generate_meeting_summary"]},
                ],
            }
        },
        "memory": {
            "enabled": True,
            "type": "execution_history",
            "stores": {"long_term": "postgres"},
        },
        "ai_config": {
            "model": "gemini-1.5-pro",
            "temperature": 0.2,
            "output_style": "meeting_report",
        },
        "actions": {"store_summary": True},
    },
]


class Command(BaseCommand):
    help = "Seed simplified templates"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, required=True)

    def handle(self, *args, **options):
        email = options["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User not found"))
            return

        for item in TEMPLATES:
            BuiltInAgent.objects.update_or_create(
                name=item["agent"]["name"],
                defaults={
                    "description": item.get("agent", {}).get("description", ""),
                    "prompt_template": item.get("agent", {}).get("prompt", ""),
                    "workflow_configuration": item.get("config", {}),
                    "input_schema": item.get("required_inputs", []),
                    "required_integrations": item.get("required_integrations", []),
                    "capabilities": item.get("agent", {}).get("capabilities", []),
                    "tools": item.get("tools", []),
                },
            )

        self.stdout.write(self.style.SUCCESS("Templates seeded successfully"))

