import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from unittest.mock import Mock, patch
import uuid

from agent.models import Agent, BuiltInAgent
from workflows.models import (
    EmailExecution,
    MeetingSummaryExecution,
    ResumeExecution,
    Workflow,
    WorkflowExecution,
)


def _create_workflow(user, agent_name, workflow_name=None):
    agent = Agent.objects.create(user=user, name=agent_name)
    workflow = Workflow.objects.create(
        agent=agent,
        name=workflow_name or f"{agent_name} Workflow",
        trigger_type="manual",
        trigger_config={},
    )
    return agent, workflow


@pytest.mark.django_db
@patch("workflows.views.create_agent_with_workflow")
def test_create_agent_and_workflow_from_template(mock_create, authenticated_client):
    client, user = authenticated_client

    template = BuiltInAgent.objects.create(
        name="Template Agent",
        description="Template description",
        prompt_template="Use this",
        workflow_configuration={"steps": []},
    )

    mock_agent = Mock()
    mock_agent.id = uuid.uuid4()
    mock_agent.name = "Generated Agent"
    mock_create.return_value = mock_agent

    response = client.post(
        reverse("workflow-create-agent-and-workflow-from-template"),
        {
            "agent_id": str(template.id),
            "configuration": "{}",
            "prompt": "Build a workflow",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["agent_id"] == str(mock_agent.id)
    assert response.data["name"] == "Generated Agent"
    mock_create.assert_called_once_with(
        user=user,
        builtin_agent=template,
        prompt_template="Build a workflow",
        configuration={},
        reference_documents=[],
    )


@pytest.mark.django_db
def test_email_executions_list_detail_and_actions(authenticated_client):
    client, user = authenticated_client
    agent, workflow = _create_workflow(user, "Email Agent", "Email Workflow")
    workflow_execution = WorkflowExecution.objects.create(
        workflow=workflow,
        status="SUCCESS",
    )
    email_execution = EmailExecution.objects.create(
        agent=agent,
        workflow_execution=workflow_execution,
        email_id="email-1",
        sender="sender@example.com",
        recipient="user@example.com",
        original_subject="Subject",
        original_body="Body",
        detected_intent="question",
        confidence_score=0.9,
        result="HUMAN_REVIEW",
        review_reason="Needs review",
    )

    list_response = client.get(reverse("email-executions-list"))
    detail_response = client.get(
        reverse("email-executions-detail", kwargs={"pk": email_execution.id})
    )

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["results"]) == 1
    assert list_response.data["results"][0]["subject"] == "Subject"
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.data["human_choice"] == "HUMAN_REVIEW"

    manual_response = client.post(
        reverse("email-executions-manual-reply", kwargs={"pk": email_execution.id}),
        {
            "subject": "Re: Subject",
            "body": "Manual reply body",
        },
        format="json",
    )

    email_execution.refresh_from_db()

    assert manual_response.status_code == status.HTTP_200_OK
    assert manual_response.data["human_choice"] == "AUTO_RESOLVED"
    assert email_execution.result == "AUTO_RESOLVED"

    delete_response = client.post(
        reverse("email-executions-delete-review", kwargs={"pk": email_execution.id})
    )

    assert delete_response.status_code == status.HTTP_200_OK
    assert not EmailExecution.objects.filter(id=email_execution.id).exists()


@pytest.mark.django_db
def test_meeting_summary_list_and_destroy(authenticated_client):
    client, user = authenticated_client
    agent, workflow = _create_workflow(user, "Meeting Notes Generator")
    workflow_execution = WorkflowExecution.objects.create(
        workflow=workflow,
        status="SUCCESS",
    )
    meeting_execution = MeetingSummaryExecution.objects.create(
        workflow_execution=workflow_execution,
        file_name="meeting.txt",
        file_path="meetings/meeting.txt",
        summary_style="concise",
        status="failed",
    )

    list_response = client.get(reverse("meeting-summary-execution-list"))

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["results"]) == 1
    assert list_response.data["results"][0]["file_name"] == "meeting.txt"

    delete_response = client.delete(
        reverse("meeting-summary-execution-detail", kwargs={"pk": meeting_execution.id})
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert not MeetingSummaryExecution.objects.filter(id=meeting_execution.id).exists()


@pytest.mark.django_db
def test_resume_execution_list_and_destroy(authenticated_client):
    client, user = authenticated_client
    agent, workflow = _create_workflow(user, "Resume Analyzer")
    workflow_execution = WorkflowExecution.objects.create(
        workflow=workflow,
        status="SUCCESS",
    )
    resume_execution = ResumeExecution.objects.create(
        workflow_execution=workflow_execution,
        file_name="resume.pdf",
        file_path="resumes/resume.pdf",
        job_title="Backend Engineer",
        job_description="Build APIs",
        status="failed",
    )

    list_response = client.get(reverse("resume-execution-list"))

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["results"]) == 1
    assert list_response.data["results"][0]["file_name"] == "resume.pdf"

    delete_response = client.delete(
        reverse("resume-execution-detail", kwargs={"pk": resume_execution.id})
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert not ResumeExecution.objects.filter(id=resume_execution.id).exists()


@pytest.mark.django_db
@patch("workflows.views.default_storage.save", return_value="resume_uploads/resume.pdf")
@patch("workflows.views.process_resume_analysis.delay")
def test_resume_analysis_execute(mock_delay, mock_save, authenticated_client):
    client, user = authenticated_client
    agent, _workflow = _create_workflow(user, "Resume Analyzer")

    upload = SimpleUploadedFile(
        "resume.pdf",
        b"resume content",
        content_type="application/pdf",
    )

    response = client.post(
        reverse("resume-analysis-execute"),
        {
            "file": upload,
            "job_title": "Backend Engineer",
            "job_description": "Build APIs",
        },
        format="multipart",
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data["agent_id"] == str(agent.id)
    assert WorkflowExecution.objects.filter(workflow__agent=agent, status="PENDING").exists()
    mock_delay.assert_called_once()
    mock_save.assert_called_once()


@pytest.mark.django_db
@patch("workflows.views.default_storage.save", return_value="meeting_notes_uploads/notes.txt")
@patch("workflows.views.process_meeting_notes_analysis.delay")
def test_meeting_notes_execute(mock_delay, mock_save, authenticated_client):
    client, user = authenticated_client
    agent, _workflow = _create_workflow(user, "Meeting Notes Generator")

    upload = SimpleUploadedFile(
        "notes.txt",
        b"meeting notes",
        content_type="text/plain",
    )

    response = client.post(
        reverse("meeting-notes-execute"),
        {
            "file": upload,
            "summary_style": "detailed",
        },
        format="multipart",
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data["agent_id"] == str(agent.id)
    assert WorkflowExecution.objects.filter(workflow__agent=agent, status="PENDING").exists()
    mock_delay.assert_called_once()
    mock_save.assert_called_once()


@pytest.mark.django_db
@patch("workflows.views.process_resume_analysis.delay")
def test_resume_analysis_retry(mock_delay, authenticated_client):
    client, user = authenticated_client
    agent, workflow = _create_workflow(user, "Resume Analyzer")
    workflow_execution = WorkflowExecution.objects.create(
        workflow=workflow,
        status="FAILED",
    )
    resume_execution = ResumeExecution.objects.create(
        workflow_execution=workflow_execution,
        file_name="resume.pdf",
        file_path="resumes/resume.pdf",
        job_title="Backend Engineer",
        job_description="Build APIs",
        status="failed",
    )

    response = client.post(
        reverse("resume-analysis-retry"),
        {"execution_id": str(resume_execution.id)},
        format="json",
    )

    workflow_execution.refresh_from_db()
    resume_execution.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert workflow_execution.status == "PENDING"
    assert resume_execution.status == "processing"
    mock_delay.assert_called_once()


@pytest.mark.django_db
@patch("workflows.views.process_meeting_notes_analysis.delay")
def test_meeting_summary_retry(mock_delay, authenticated_client):
    client, user = authenticated_client
    agent, workflow = _create_workflow(user, "Meeting Notes Generator")
    workflow_execution = WorkflowExecution.objects.create(
        workflow=workflow,
        status="FAILED",
    )
    meeting_execution = MeetingSummaryExecution.objects.create(
        workflow_execution=workflow_execution,
        file_name="meeting.txt",
        file_path="meetings/meeting.txt",
        summary_style="concise",
        status="failed",
    )

    response = client.post(
        reverse("meeting-summary-retry"),
        {"execution_id": str(meeting_execution.id)},
        format="json",
    )

    workflow_execution.refresh_from_db()
    meeting_execution.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert workflow_execution.status == "PENDING"
    assert meeting_execution.status == "processing"
    mock_delay.assert_called_once()
