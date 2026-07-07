from langchain_core.prompts import ChatPromptTemplate
from services.llm_service import llm

PROMPT = """
Analyze market trend data.

Payload:

{payload}

Identify:

- trends
- opportunities
- threats
- innovation signals

Return JSON.
"""


def market_trends_task(payload):

    chain = ChatPromptTemplate.from_template(PROMPT) | llm

    response = chain.invoke({"payload": payload})

    return response.content
