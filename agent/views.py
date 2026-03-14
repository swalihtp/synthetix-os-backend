# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import status

# from .serializers import AgentCreateSerializer, AgentSerializer
# from .services.agent_planner import AgentPlanner
# from .services.agent_factory import AgentFactory
# from .models import AgentTrigger
# from .tasks import execute_agent_task


# class AgentCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = AgentCreateSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         planner = AgentPlanner()
#         try:
#             plan = planner.generate_plan(serializer.validated_data["goal_prompt"])
#         except Exception as e:
#             return Response({"error": "Failed to generate automation plan", "details": str(e)},status=400)

#         factory = AgentFactory()
#         agent = factory.create_from_plan(
#             user=request.user,
#             name=serializer.validated_data["name"],
#             goal_prompt=serializer.validated_data["goal_prompt"],
#             plan=plan,
#         )

#         return Response(
#             AgentSerializer(agent).data,
#             status=status.HTTP_201_CREATED,
#         )
        
# class AgentListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         agents = request.user.agents.all()
#         return Response(AgentSerializer(agents, many=True).data)
    
# class AgentStatusUpdateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def patch(self, request, pk):
#         agent = request.user.agents.get(id=pk)

#         new_status = request.data.get("status")
#         agent.status = new_status
#         agent.save()

#         return Response({"status": "updated"})
    
# class GmailWebhookView(APIView):

#     def post(self, request):
#         payload = request.data

#         # Find matching trigger
#         triggers = AgentTrigger.objects.filter(
#             trigger_type="gmail",
#             is_active=True
#         )

#         for trigger in triggers:
#             execute_agent_task.delay(
#                 str(trigger.agent.id),
#                 payload
#             )

#         return Response({"status": "received"})


from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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