import logging
from pathlib import Path
from celery import shared_task
from django.contrib.auth import get_user_model
from workflows.gmail_notification.graph import gmail_notification_app
from workflows.email_workflow.graph import email_workflow_app
from workflows.resume_analyzer_workflow.graph import resume_analyzer_app
from workflows.meeting_notes_generator_workflow.graph import meeting_notes_app
from agent.models import Agent, AgentDocuments
from workflows.market_inteligence_workflow.new_graph import market_intelligence_app
from .models import WorkflowExecution, ResumeExecution, MeetingSummaryExecution
from django.utils import timezone
import httplib2
from googleapiclient.errors import HttpError
from google.auth.exceptions import TransportError
from agent.models import AgentDocuments
import requests
from django.conf import settings
from .market_inteligence_workflow.services.document_service import load_documents
from workflows.models import EmailExecution
from integrations.gmail import send_reply
from .email_workflow.services.ai.ai_service import store_document_in_croma_db
from workflows.utils.realtime import send_workflow_update

logger = logging.getLogger(__name__)
User = get_user_model()


# @shared_task
# def renew_gmail_watches():
#     """Renew Gmail watch for all users with Gmail integration."""

#     integrations = Integration.objects.filter(provider="gmail", is_active=True)

#     for integration in integrations:
#         try:
#             register_gmail_watch(integration.user)
#             print(f"[Gmail Watch] Renewed for {integration.user.email}")
#         except Exception as e:
#             print(f"[Gmail Watch] Failed for {integration.user.email}: {e}")


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_gmail_notification_task(self, state):
    try:
        res = gmail_notification_app.invoke(state)
        return res
    except (OSError, httplib2.ServerNotFoundError, TransportError) as e:
        # Transient network errors - retry with exponential backoff
        raise self.retry(exc=e, countdown=2**self.request.retries * 10)
    except HttpError as e:
        if e.resp.status in [429, 500, 502, 503, 504]:
            # Google API rate limit or server error - retry
            raise self.retry(exc=e, countdown=2**self.request.retries * 10)
        # Other HTTP errors (400, 401 etc) - don't retry, just fail
        raise


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_email_task(self, message_id, user_id):
    try:
        agent = Agent.objects.prefetch_related("workflows").get(
            user__id=user_id, name__iexact="Smart Email Agent"
        )
        workflow = agent.workflows.first()

        if not workflow:
            raise Exception("No workflow found for agent")

        execution = WorkflowExecution.objects.create(
            workflow=workflow, status="RUNNING"
        )

        state = {
            "email_id": message_id,
            "user_id": user_id,
            "agent_id": str(agent.id),
            "execution_id": str(execution.id),
        }
        return email_workflow_app.invoke(state)

    except Exception as exc:

        if self.request.retries >= self.max_retries:
            execution.status = "FAILED"
            execution.ended_at = timezone.now()
            execution.error_message = str(exc)
            execution.save()

        raise self.retry(exc=exc)


@shared_task
def run_market_intelligence():

    try:

        agents = Agent.objects.filter(
            name__iexact="Market Intelligence Agent", is_active=True
        ).select_related("user")

        for agent in agents:
            docs = list(
                AgentDocuments.objects.filter(agent=agent).values_list(
                    "document", flat=True
                )
            )
            company_name = agent.agent_schema.get("company_name", "")
            company_website = agent.agent_schema.get("company_website", "")
            company_description = agent.agent_schema.get("company_description", "")

            state = {
                "company_name": company_name,
                "company_description": company_description,
                "company_website": company_website,
                "document_ids": docs,
            }

            market_intelligence_app.invoke(state)

    except Exception as e:
        print(f"Error creating executions: {str(e)}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(requests.exceptions.RequestException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def ingest_documents_to_vector_db(
    self,
    agent_id,
    document_ids,
    user_id,
):
    documents = AgentDocuments.objects.filter(id__in=document_ids)

    documents.update(status="processing")

    payload = {
        "agent_id": agent_id,
        "user_id": user_id,
        "documents": [],
    }

    try:
        for document in documents:

            extracted = load_documents([document.document.path])

            text = extracted[0]["content"]

            payload["documents"].append(
                {
                    "document_id": str(document.id),
                    "filename": document.original_name,
                    "content": text,
                }
            )

        response = requests.post(
            f"{settings.AI_SERVICE_URL}/api/documents/ingest",
            json=payload,
            timeout=300,
        )

        response.raise_for_status()

        documents.update(status="completed")

        print(f"RESULT FORM CELERY TASK:{payload}")

    except Exception:
        documents.update(status="failed")
        raise

@shared_task(bind=True, max_retries=3)
def send_manual_reply_task(self, execution_id):
    try:
        execution = EmailExecution.objects.select_related("agent__user").get(
            id=execution_id
        )

        send_reply(
            user=execution.agent.user,
            to=execution.sender,
            subject=execution.reply_subject,
            body=execution.reply_body,
            thread_id=execution.thread_id,
            in_reply_to=execution.email_id,
        )

        return {
            "success": True,
            "execution_id": execution_id,
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def store_email_memory_task(self, execution_id):
    try:
        execution = EmailExecution.objects.select_related("agent__user").get(
            id=execution_id
        )

        raw_email = {
            "subject": execution.original_subject,
            "body": execution.original_body,
            "from": execution.sender,
            "thread_id": execution.thread_id,
            "message_id": execution.email_id,
        }

        result = store_document_in_croma_db(
            raw_email=raw_email,
            reply_subject=execution.reply_subject,
            reply_text=execution.reply_body,
            user_id=str(execution.agent.user.id),
        )

        return result

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=60,
        )

@shared_task(bind=True, max_retries=3)
def process_resume_analysis(self, file_path, execution_id, job_title, job_description):
    workflow_execution = None
    resume_execution = None

    try:
        workflow_execution = WorkflowExecution.objects.get(id=execution_id)

        resume_execution, _ = ResumeExecution.objects.get_or_create(
            workflow_execution=workflow_execution,
            defaults={
                "file_name": Path(file_path).name,
                "file_type": Path(file_path).suffix.lstrip("."),
                "file_path": file_path,
                "job_title": job_title,
                "job_description": job_description,
                "status": "processing",
            },
        )

        resume_execution.status = "processing"
        resume_execution.file_name = resume_execution.file_name or Path(file_path).name
        resume_execution.file_type = resume_execution.file_type or Path(file_path).suffix.lstrip(".")
        resume_execution.file_path = file_path
        resume_execution.job_title = job_title or resume_execution.job_title
        resume_execution.job_description = (
            job_description or resume_execution.job_description
        )
        resume_execution.save(
            update_fields=[
                "status",
                "file_name",
                "file_type",
                "file_path",
                "job_title",
                "job_description",
            ]
        )

        state = {
            "file_path": file_path,
            "file_type": Path(file_path).suffix.lstrip("."),
            "execution_id": str(execution_id),
            "job_title": job_title,
            "job_description": job_description,
        }

        return resume_analyzer_app.invoke(state)

    except Exception as exc:
        if resume_execution:
            resume_execution.status = "failed"
            resume_execution.error_message = str(exc)
            resume_execution.save(update_fields=["status", "error_message"])

        if workflow_execution:
            workflow_execution.status = "FAILED"
            workflow_execution.ended_at = timezone.now()
            workflow_execution.error_message = str(exc)
            workflow_execution.save(
                update_fields=["status", "ended_at", "error_message"]
            )

            send_workflow_update(
                workflow_execution.workflow.agent_id,
                {
                    "event": "resume_analysis_failed",
                    "workflow_execution_id": str(workflow_execution.id),
                    "resume_execution_id": str(resume_execution.id)
                    if resume_execution
                    else None,
                    "status": "failed",
                    "message": str(exc),
                },
            )

        raise


@shared_task(bind=True, max_retries=3)
def process_meeting_notes_analysis(self, file_path, execution_id, summary_style):
    workflow_execution = None
    meeting_execution = None

    try:
        workflow_execution = WorkflowExecution.objects.get(id=execution_id)

        meeting_execution, _ = MeetingSummaryExecution.objects.get_or_create(
            workflow_execution=workflow_execution,
            defaults={
                "file_name": Path(file_path).name,
                "file_type": Path(file_path).suffix.lstrip("."),
                "file_path": file_path,
                "summary_style": summary_style,
                "status": "processing",
            },
        )

        meeting_execution.status = "processing"
        meeting_execution.file_name = meeting_execution.file_name or Path(file_path).name
        meeting_execution.file_type = (
            meeting_execution.file_type or Path(file_path).suffix.lstrip(".")
        )
        meeting_execution.file_path = file_path
        meeting_execution.summary_style = summary_style or meeting_execution.summary_style
        meeting_execution.save(
            update_fields=[
                "status",
                "file_name",
                "file_type",
                "file_path",
                "summary_style",
            ]
        )

        state = {
            "file_path": file_path,
            "file_type": Path(file_path).suffix.lstrip("."),
            "execution_id": str(execution_id),
            "summary_style": summary_style,
        }

        return meeting_notes_app.invoke(state)

    except Exception as exc:
        if meeting_execution:
            meeting_execution.status = "failed"
            meeting_execution.error_message = str(exc)
            meeting_execution.save(update_fields=["status", "error_message"])

        if workflow_execution:
            workflow_execution.status = "FAILED"
            workflow_execution.ended_at = timezone.now()
            workflow_execution.error_message = str(exc)
            workflow_execution.save(
                update_fields=["status", "ended_at", "error_message"]
            )

            send_workflow_update(
                workflow_execution.workflow.agent_id,
                {
                    "event": "meeting_notes_failed",
                    "workflow_execution_id": str(workflow_execution.id),
                    "meeting_execution_id": str(meeting_execution.id)
                    if meeting_execution
                    else None,
                    "status": "failed",
                    "message": str(exc),
                },
            )

        raise
