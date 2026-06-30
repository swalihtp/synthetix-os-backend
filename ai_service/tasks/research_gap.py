from langchain_core.prompts import ChatPromptTemplate
from services.llm_service import llm

PROMPT = """
Review company profile.

Identify missing information.

Possible gaps:

- pricing
- products
- services
- customers
- geography
- competitors

Payload:

{payload}

Return JSON list.
"""


def research_gap_task(payload):

    chain = ChatPromptTemplate.from_template(PROMPT) | llm

    response = chain.invoke({"payload": payload})

    return response.content
