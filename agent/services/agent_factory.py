from agent.models import Agent, AgentTrigger, AgentAction

class AgentFactory:

    def create_from_plan(self, user, name, goal_prompt, plan: dict):
        agent = Agent.objects.create(
            user=user,
            name=name,
            goal_prompt=goal_prompt,
        )

        # Create trigger
        AgentTrigger.objects.create(
            agent=agent,
            trigger_type=plan["trigger"]["tool"],
            config=plan["trigger"],
        )

        # Create actions
        for action in plan["actions"]:
            AgentAction.objects.create(
                agent=agent,
                action_type=action["tool"],
                config=action,
            )

        return agent