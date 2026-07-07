# Synthetix OS Backend

Synthetix OS is a Django-based automation platform with a separate FastAPI AI microservice. It is built to run AI-powered agents, workflow executions, Gmail-driven automations, document ingestion, and admin analytics from one backend.

## What This Project Contains

- `accounts/` for email-based auth, JWT login, password reset, MFA, Google login, and email verification
- `agent/` for user agents, built-in agent templates, agent documents, and agent execution tracking
- `workflows/` for workflow definitions, workflow executions, email processing, resume analysis, meeting notes, and market intelligence orchestration
- `integrations/` for Gmail OAuth, Gmail watch registration, and integration status tracking
- `persona/` for user persona and AI preference profiles
- `dashboard/` for the authenticated user dashboard
- `system_admin/` for system admin statistics, user management, invitations, and usage analytics
- `triggers/` for Gmail Pub/Sub webhook handling
- `ai-service/` for the standalone FastAPI service that performs LLM-powered analysis tasks

## High-Level Architecture

- Django REST Framework handles the main API surface.
- JWT authentication is used for API access.
- Channels provides websocket updates for agent workflows.
- Celery handles asynchronous workflow jobs.
- Redis is used for Celery broker/result backend and channel layers.
- PostgreSQL stores application data.
- The AI microservice runs separately on port `8001` and is called by the Django app for model-driven tasks.

## Main Capabilities

- Email automation with intent detection, retrieval-based context, reply generation, and human review support
- Market intelligence workflows that research a company, competitors, trends, sentiment, SWOT, and generate PDF reports
- Resume analysis with structured feedback, skill evaluation, and ATS scoring
- Meeting note generation from transcripts with topics, decisions, action items, and summaries
- Gmail integration with OAuth and watch registration
- User persona capture for personalized AI behavior
- System admin analytics for workflow execution and AI usage
- Real-time workflow updates over websockets

## Workflow Overview

- Email workflow: Gmail notification -> email processing -> intent analysis -> context retrieval -> reply generation -> optional human review -> send reply -> store memory
- Resume workflow: upload resume -> extract text -> analyze structure and skills -> score ATS fit -> store execution result
- Meeting notes workflow: upload transcript -> extract text -> detect topics and decisions -> generate summary -> store execution result
- Market intelligence workflow: load configuration -> fetch company and competitor data -> run analysis stages -> generate report -> render PDF -> upload to S3 -> send report

## Backend API Routes

The Django app exposes the following route groups:

- `GET /api/schema/`
- `GET /api/docs/swagger/`
- `GET /api/docs/redoc/`
- `POST /api/token/`
- `/api/auth/`
- `/api/agent/`
- `/api/workflows/`
- `/api/integrations/`
- `/api/email/webhook/`
- `/api/persona/`
- `/api/dashboard/`
- `/api/system-admin/`

Important route examples:

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `POST /api/auth/refresh/`
- `GET|PUT /api/auth/me/`
- `POST /api/auth/mfa/enable/`
- `POST /api/auth/mfa/setup/verify/`
- `POST /api/auth/mfa/login/verify/`
- `POST /api/auth/auth/google/`
- `GET /api/agent/<uuid>/dashboard/`
- `POST /api/agent/<uuid>/...` via the agent router
- `POST /api/workflows/create-agent-and-workflow-from-template/`
- `POST /api/workflows/resume-executions/analyze/`
- `POST /api/workflows/resume-executions/retry/`
- `POST /api/workflows/meeting-notes-executions/analyze/`
- `POST /api/workflows/meeting-summary-executions/retry/`
- `GET /api/integrations/gmail/connect/`
- `GET /api/integrations/gmail/callback/`
- `POST /api/integrations/gmail/watch/`
- `GET /api/system-admin/dashboard/statistics/`
- `POST /api/system-admin/analytics/snapshot/`
- `GET /api/system-admin/workflows/stats/`
- `GET /api/system-admin/ai-usage/dashboard/`
- `GET /api/system-admin/email-activity/`
- `GET /api/system-admin/users/`
- `GET /api/system-admin/users/<uuid>/`
- `PATCH /api/system-admin/users/<uuid>/block/`
- `PATCH /api/system-admin/users/<uuid>/activate/`
- `DELETE /api/system-admin/users/<uuid>/delete/`
- `POST /api/system-admin/create-admin/`
- `POST /api/system-admin/accept-invite/`

Websocket:

- `ws/agents/<agent_id>/`

## AI Service Routes

The FastAPI service in `ai-service/` exposes:

- `GET /health`
- `POST /api/analyze-intention`
- `POST /api/process-email`
- `POST /api/store-doc`
- `POST /api/analyze-resume`
- `POST /api/generate-meeting-summary`
- `POST /api/summarize`
- `POST /api/execute`
- `POST /api/documents/ingest`
- `POST /api/market-inteligence/generate-plan`
- `POST /api/market-inteligence/analyze-market`
- `POST /api/market-inteligence/analyze-competitors`
- `POST /api/market-inteligence/analyze-trends`
- `POST /api/market-inteligence/analyze-sentiment`
- `POST /api/market-inteligence/analyze-swot`
- `POST /api/market-inteligence/generate-report`

Note: the market intelligence prefix is spelled `market-inteligence` in the code.

## Built-In Agent Templates

The repository includes seeded templates for:

- Smart Email Agent
- Market Intelligence Agent
- Resume Analyzer
- Meeting Notes Generator

Use the seeding command after creating a user:

```bash
cd backend
python manage.py seed_templates --email your@email.com
```

RBAC seed command:

```bash
cd backend
python manage.py seed_rbac
```

## Local Setup

### Recommended: Docker Compose

```bash
docker compose up --build
```

This starts:

- PostgreSQL with pgvector
- Redis
- Django backend on port `8000`
- Celery worker
- Celery beat
- FastAPI AI service on port `8001`

### Manual Setup

Backend:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements/core.txt
pip install -r requirements/integrations.txt
cd backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Celery:

```bash
celery -A synthetix_os worker --loglevel=info
celery -A synthetix_os beat --loglevel=info
```

AI service:

```bash
cd ai-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

## Settings

The Django project uses these settings modules:

- `synthetix_os.settings.dev` for local development
- `synthetix_os.settings.prod` for production

The default ASGI and Celery entry points point to the dev settings module unless overridden by `DJANGO_SETTINGS_MODULE`.

## Environment Variables

Backend and shared runtime:

- `SECRET_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `REDIS_URL`
- `AI_SERVICE_URL`
- `FRONTEND_URL`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `HF_API_KEY`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_SIGNATURE_NAME`
- `AWS_S3_REGION_NAME`
- `LAMBDA_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `GOOGLE_CLOUD_PROJECT_ID`
- `TELEGRAM_BOT_TOKEN`
- `TAVILY_API_KEY`
- `FIRECRAWL_API_KEY`

AI service:

- `OPEN_ROUTER_API_KEY`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`

Production-only or deployment-specific:

- `ALLOWED_HOSTS`
- `CORS_ORIGINS`

## Key Data Models

- `accounts.User`, `Role`, `Permission`, `EmailVerification`
- `agent.BuiltInAgent`, `Agent`, `AgentDocuments`, `AgentExecution`, `S3MarketIntelligenceReport`
- `workflows.Workflow`, `WorkflowExecution`, `EmailExecution`, `EmailAttachment`, `WorkflowForHumanReview`, `ResumeExecution`, `MeetingSummaryExecution`, `AIUsageLog`, `DailyAIUsageSnapshot`
- `integrations.Integration`, `V2Integration`, `ProcessedEmail`, `GmailSync`
- `persona.UserPersona`
- `system_admin.AdminInvitation`

## Testing

```bash
pytest
```

The repository also includes focused tests under `accounts/`, `agent/`, `workflows/`, `integrations/`, `dashboard/`, `system_admin/`, and `triggers/`.

## Notes

- The backend uses `channels_redis` for websocket groups.
- The market intelligence workflow uses external services such as Tavily, Firecrawl, S3, and document extraction helpers.
- Uploaded files and generated reports are stored in the repository's media/report directories during development.
- The repo includes sample generated reports and agent documents, which are useful for testing but not required for a clean deployment.

## License

MIT
