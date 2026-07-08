from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Workflow
from .serializers import (
    WorkflowSerializer,
    WorkflowCreateSerializer,
    EmailExecutionListSerializer,
    EmailExecutionDetailSerializer,
    ResumeExecutionSerializer,
    MeetingSummaryExecutionSerializer,
    MeetingNotesInputSerializer,
    ResumeAnalysisInputSerializer,
    RetryExecutionSerializer
)
from .models import (
    EmailExecution,
    ResumeExecution,
    MeetingSummaryExecution,
    WorkflowExecution,
    Workflow,
)
from .filters import MeetingSummaryExecutionFilter, ResumeExecutionFilter
from agent.models import BuiltInAgent
from .services.workflow_builder import create_agent_with_workflow
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import IntegrityError
from .pagination import HumanReviewPagination
from rest_framework import status
from .tasks import (
    send_manual_reply_task,
    store_email_memory_task,
    process_resume_analysis,
    process_meeting_notes_analysis,
)
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage


class WorkflowViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workflow.objects.filter(agent__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return WorkflowCreateSerializer
        return WorkflowSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    @action(
        detail=False,
        methods=["post"],
        url_path="create-agent-and-workflow-from-template",
    )
    def create_agent_and_workflow_from_template(self, request):

        template_id = request.data.get("agent_id")

        if not template_id:
            return Response({"error": "agent_id is required"}, status=400)

        try:
            template = BuiltInAgent.objects.get(id=template_id)

        except BuiltInAgent.DoesNotExist:
            return Response({"error": "Template not found"}, status=404)

        raw_configuration = request.data.get("configuration", "{}")

        try:
            configuration = json.loads(raw_configuration)

        except json.JSONDecodeError:
            return Response({"error": "Invalid configuration JSON"}, status=400)

        reference_documents = request.FILES.getlist("reference_documents")

        print(f"REFERENCE DOCUMENTS: {reference_documents}")
        try:

            agent = create_agent_with_workflow(
                user=request.user,
                builtin_agent=template,
                prompt_template=request.data.get("prompt"),
                configuration=configuration,
                reference_documents=reference_documents,
            )

        except IntegrityError:
            return Response(
                {"error": "Agent with this name already exists"}, status=400
            )

        return Response(
            {
                "message": "Agent created successfully",
                "agent_id": str(agent.id),
                "name": agent.name,
            },
            status=201,
        )


class EmailExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = HumanReviewPagination

    def get_queryset(self):
        qs = (
            EmailExecution.objects.filter(agent__user=self.request.user)
            .prefetch_related("attachments")
            .order_by("-processed_at")
        )

        agent_id = self.request.query_params.get("agent_id")
        if agent_id:
            qs = qs.filter(agent_id=agent_id)

        result = self.request.query_params.get("result")

        if result and result != "ALL":
            qs = qs.filter(result=result)

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EmailExecutionDetailSerializer

        return EmailExecutionListSerializer

    @action(detail=True, methods=["post"], url_path="manual-reply")
    def manual_reply(self, request, pk=None):
        review = self.get_object()

        subject = request.data.get("subject")
        body = request.data.get("body")

        if not subject or not body:
            return Response(
                {"error": "Subject and body are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review.reply_subject = subject
        review.reply_body = body
        review.result = "AUTO_RESOLVED"

        review.save(
            update_fields=[
                "reply_subject",
                "reply_body",
                "result",
            ]
        )

        send_manual_reply_task.delay(review.id)
        store_email_memory_task.delay(review.id)

        serializer = EmailExecutionDetailSerializer(review)

        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="delete")
    def delete_review(self, request, pk=None):
        review = self.get_object()

        review.delete()

        return Response(
            {"message": "Review deleted successfully"},
            status=status.HTTP_200_OK,
        )


class MeetingSummaryExecutionViewSet(
    viewsets.ReadOnlyModelViewSet, mixins.DestroyModelMixin
):
    serializer_class = MeetingSummaryExecutionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HumanReviewPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MeetingSummaryExecutionFilter
    ordering_fields = ["created_at", "updated_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            MeetingSummaryExecution.objects.select_related(
                "workflow_execution",
                "workflow_execution__workflow",
                "workflow_execution__workflow__agent",
            )
            .filter(workflow_execution__workflow__agent__user=self.request.user)
            .order_by("-created_at")
        )


class MeetingNotesExecutionView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = MeetingNotesInputSerializer

    def create(self, request, *args, **kwargs):
        print("Made chages in meeting notes")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = Workflow.objects.get(
            agent__name="Meeting Notes Generator", agent__user=request.user
        )

        file = serializer.validated_data["file"]
        summary_style = serializer.validated_data.get("summary_style", "concise")

        file_path = default_storage.save(
            f"meeting_notes_uploads/{file.name}",
            file,
        )

        workflow_execution = WorkflowExecution.objects.create(
            workflow=workflow, status="PENDING"
        )

        process_meeting_notes_analysis.delay(
            execution_id=str(workflow_execution.id),
            file_path=file_path,
            summary_style=summary_style,
        )

        return Response(
            {
                "message": "Meeting notes analysis started",
                "workflow_execution_id": str(workflow_execution.id),
                "agent_id": str(workflow.agent.id),
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ResumeAnalysisExecutionView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ResumeAnalysisInputSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = Workflow.objects.get(
            agent__name="Resume Analyzer", agent__user=request.user
        )

        file = serializer.validated_data["file"]
        job_title = serializer.validated_data["job_title"]
        job_description = serializer.validated_data["job_description"]

        file_path = default_storage.save(
            f"resume_uploads/{file.name}",
            file,
        )

        workflow_execution = WorkflowExecution.objects.create(
            workflow=workflow, status="PENDING"
        )

        process_resume_analysis.delay(
            execution_id=str(workflow_execution.id),
            job_title=job_title,
            job_description=job_description,
            file_path=file_path,
        )

        return Response(
            {
                "message": "Resume analysis started",
                "workflow_execution_id": str(workflow_execution.id),
                "agent_id": str(workflow.agent.id),
            },
            status=status.HTTP_202_ACCEPTED,
        )


class _BaseWorkflowExecutionRetryView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RetryExecutionSerializer

    def get_execution(self, execution_id):
        raise NotImplementedError

    def reset_execution(self, workflow_execution, execution):
        workflow_execution.status = "PENDING"
        workflow_execution.ended_at = None
        workflow_execution.error_message = None
        workflow_execution.save(
            update_fields=["status", "ended_at", "error_message"]
        )

        execution.status = "processing"
        execution.error_message = None
        execution.save(update_fields=["status", "error_message"])

    def handle_retry(self, workflow_execution, execution):
        raise NotImplementedError

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        execution_id = serializer.validated_data["execution_id"]

        try:
            execution, workflow_execution = self.get_execution(execution_id)
        except self.execution_not_found_exception:
            return Response(
                {"error": self.execution_not_found_message},
                status=status.HTTP_404_NOT_FOUND,
            )
        except WorkflowExecution.DoesNotExist:
            return Response(
                {"error": "Workflow execution not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not execution:
            return Response(
                {"error": "Execution not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (execution.status or "").lower() != "failed":
            return Response(
                {"error": "Only failed executions can be retried"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.handle_retry(workflow_execution, execution)


class ResumeAnalysisRetryView(_BaseWorkflowExecutionRetryView):
    execution_not_found_exception = ResumeExecution.DoesNotExist
    execution_not_found_message = "Resume execution not found"

    def get_execution(self, execution_id):
        execution = ResumeExecution.objects.select_related("workflow_execution__workflow__agent").get(
            id=execution_id,
            workflow_execution__workflow__agent__user=self.request.user,
        )
        print(f"EXECUTION GOT:f{execution}")
        return execution, execution.workflow_execution

    def handle_retry(self, workflow_execution, execution):
        if not execution.file_path or not execution.job_title or not execution.job_description:
            return Response(
                {"error": "Missing stored resume inputs for retry"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.reset_execution(workflow_execution, execution)

        process_resume_analysis.delay(
            execution_id=str(workflow_execution.id),
            file_path=execution.file_path,
            job_title=execution.job_title,
            job_description=execution.job_description,
        )

        return Response(
            {
                "message": "Resume analysis retry started",
                "workflow_execution_id": str(workflow_execution.id),
                "resume_execution_id": str(execution.id),
                "status": "PENDING",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class MeetingSummaryRetryView(_BaseWorkflowExecutionRetryView):
    execution_not_found_exception = MeetingSummaryExecution.DoesNotExist
    execution_not_found_message = "Meeting summary execution not found"

    def get_execution(self, execution_id):
        execution = MeetingSummaryExecution.objects.select_related(
            "workflow_execution__workflow__agent"
        ).get(
            id=execution_id,
            workflow_execution__workflow__agent__user=self.request.user,
        )
        return execution, execution.workflow_execution

    def handle_retry(self, workflow_execution, execution):
        if not execution.file_path:
            return Response(
                {"error": "Missing stored meeting inputs for retry"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.reset_execution(workflow_execution, execution)

        process_meeting_notes_analysis.delay(
            execution_id=str(workflow_execution.id),
            file_path=execution.file_path,
            summary_style=execution.summary_style,
        )

        return Response(
            {
                "message": "Meeting summary retry started",
                "workflow_execution_id": str(workflow_execution.id),
                "meeting_execution_id": str(execution.id),
                "status": "PENDING",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ResumeExecutionViewSet(viewsets.ReadOnlyModelViewSet, mixins.DestroyModelMixin):
    serializer_class = ResumeExecutionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HumanReviewPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ResumeExecutionFilter
    ordering_fields = ["created_at", "updated_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            ResumeExecution.objects.select_related(
                "workflow_execution",
                "workflow_execution__workflow",
                "workflow_execution__workflow__agent",
            )
            .filter(workflow_execution__workflow__agent__user=self.request.user)
            .order_by("-created_at")
        )
