# from agent.models import AgentRun, AgentStep
# from django.utils import timezone


# class AgentExecutor:

#     def execute(self, agent, trigger_payload):
#         run = AgentRun.objects.create(
#             agent=agent,
#             trigger_event=trigger_payload,
#             status="running",
#             started_at=timezone.now(),
#         )

#         try:
#             # Step 1: Analyze event
#             AgentStep.objects.create(
#                 run=run,
#                 step_order=1,
#                 thought="Analyzing incoming event."
#             )

#             # Here call LLM runtime logic (later expand)
#             # Then call tool router

#             run.status = "success"
#             run.completed_at = timezone.now()
#             run.save()

#         except Exception as e:
#             run.status = "failed"
#             run.error_message = str(e)
#             run.save()

#         return run