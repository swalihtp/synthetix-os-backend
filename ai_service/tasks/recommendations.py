from langchain_core.prompts import ChatPromptTemplate
from services.llm_service import llm

PROMPT = """
Generate strategic recommendations.

Payload:

{payload}

Generate:

- immediate actions
- short term actions
- long term actions
- risks

Return JSON.
"""


def recommendations_task(payload):

    chain = ChatPromptTemplate.from_template(PROMPT) | llm

    response = chain.invoke({"payload": payload})

    return response.content
