from langchain_core.prompts import ChatPromptTemplate
from services.llm_service import llm

PROMPT = """
Analyze competitor.

Payload:

{payload}

Extract:

- company name
- products
- services
- strengths
- weaknesses
- positioning

Return JSON.
"""


def competitor_analysis_task(payload):

    chain = ChatPromptTemplate.from_template(PROMPT) | llm

    response = chain.invoke({"payload": payload})

    return response.content
