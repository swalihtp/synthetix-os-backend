from django.db import transaction
from agent.models import Agent, AgentDocuments
from workflows.models import Workflow
from workflows.tasks import ingest_documents_to_vector_db


@transaction.atomic
def create_agent_with_workflow(
    user,
    builtin_agent,
    prompt_template=None,
    configuration=None,
    reference_documents=None,
):
    configuration = configuration or {}
    reference_documents = reference_documents or []

    workflow_config = builtin_agent.workflow_configuration or {}

    # Create Agent
    agent = Agent.objects.create(
        user=user,
        name=builtin_agent.name,
        description=builtin_agent.description,
        prompt=prompt_template or builtin_agent.prompt_template,
        template=builtin_agent,
        agent_schema=configuration or {},
    )

    # Save uploaded documents
    document_ids = []
    for file in reference_documents:
        agent_document = AgentDocuments.objects.create(
            agent=agent,
            document=file,
            original_name=file.name,
        )
        document_ids.append(str(agent_document.id))

    transaction.on_commit(
        lambda: ingest_documents_to_vector_db.delay(
            agent_id=str(agent.id),
            document_ids=document_ids,
            user_id=str(user.id),
        )
    )

    # Extract trigger config
    trigger = workflow_config.get("trigger", {})

    # Create Workflow
    workflow = Workflow.objects.create(
        agent=agent,
        name=f"{agent.name} Workflow",
        trigger_type=trigger.get("type", "manual"),
        schedule=trigger.get("schedule"),
        trigger_config={
            "type": trigger.get("type"),
            "filters": trigger.get("filters", {}),
        },
        config={
            "template_config": workflow_config,
            "user_configuration": configuration,
        },
    )

    return agent
