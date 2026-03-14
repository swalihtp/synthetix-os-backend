# from celery import shared_task
# from .models import Agent
# from .services.agent_executor import AgentExecutor


# @shared_task
# def execute_agent_task(agent_id, trigger_payload):
#     agent = Agent.objects.get(id=agent_id)

#     executor = AgentExecutor()
#     executor.execute(agent, trigger_payload)