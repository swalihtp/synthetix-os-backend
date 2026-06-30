from workflows.email_workflow.state import EmailWorkflowState
from agent.models import Agent


def initial_node(state: EmailWorkflowState) -> EmailWorkflowState:
    agent = Agent.objects.get(id=state.get("agent_id"))
    print(f"AGENT ID CHECKING: {str(agent.id)} ")

    schema = agent.agent_schema or {}

    emails_should_ai_reply_to = schema.get("ai_reply_categories", [])
    emails_should_be_sent_for_human_review = schema.get("human_review_categories", [])
    emails_should_AI_ignore = schema.get("ignore_rules", [])

    return {
        "ai_reply_categories": emails_should_ai_reply_to,
        "human_review_categories": emails_should_be_sent_for_human_review,
        "ignore_categories": emails_should_AI_ignore,
    }
