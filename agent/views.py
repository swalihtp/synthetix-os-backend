from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import httpx
from django.conf import settings
from .models import Agent
from .serializers import AgentSerializer, AgentCreateSerializer


class AgentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Agent.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AgentCreateSerializer
        return AgentSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['post'], url_path='generate')
    def generate_workflow(self, request):
        prompt = request.data.get('prompt', '')
        name = request.data.get('name', 'AI Generated Agent')

        if not prompt:
            return Response(
                {"error": "prompt is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ai_response = httpx.post(
                f"{settings.AI_SERVICE_URL}/workflow/generate",
                json={"prompt": prompt},
                timeout=30.0,
            )
            ai_response.raise_for_status()
            workflow_data = ai_response.json()

            # DEBUG — remove after fix
            print(f"[Generate] AI returned: {workflow_data}")
            print(f"[Generate] Steps: {workflow_data.get('steps')}")

        except Exception as e:
            return Response(
                {"error": f"AI service error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not workflow_data.get("steps"):
            return Response(
                {"error": f"AI generated invalid workflow — no steps found. Got: {workflow_data}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


        # Step 3 — Create Agent
        agent = Agent.objects.create(
            user=request.user,
            name=name,
            description=f"AI-generated agent: {prompt[:200]}",
            prompt=prompt,
        )
        # Step 4 — Create Workflow and Steps
        from workflows.models import Workflow, WorkflowStep
        workflow = Workflow.objects.create(
            agent=agent,
            name=workflow_data.get("name", name),
            trigger_type=workflow_data.get("trigger_type", "api.trigger"),
            trigger_config=workflow_data.get("trigger_config", {}),
        )
        steps = workflow_data.get("steps", [])
        for step_data in steps:
            WorkflowStep.objects.create(
                workflow=workflow,
                step_type=step_data.get("step_type", "system"),
                action=step_data.get("action", ""),
                config=step_data.get("config", {}),
                order=step_data.get("order", 1),
                on_failure=step_data.get("on_failure", "stop"),
            )
        # Step 5 — Return the created agent and workflow
        return Response({
            "message": "Agent and workflow created successfully!",
            "agent": {
                "id": str(agent.id),
                "name": agent.name,
                "prompt": agent.prompt,
            },
            "workflow": {
                "id": str(workflow.id),
                "name": workflow.name,
                "trigger_type": workflow.trigger_type,
                "steps_count": len(steps),
                "steps": [
                    {
                        "order": s.get("order"),
                        "action": s.get("action"),
                        "step_type": s.get("step_type"),
                    }
                    for s in steps
                ],
            },
        }, status=status.HTTP_201_CREATED)