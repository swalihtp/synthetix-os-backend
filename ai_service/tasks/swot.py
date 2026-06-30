from langchain_core.prompts import ChatPromptTemplate
from services.llm_service import llm

PROMPT = """
Generate SWOT analysis.

Payload:

{payload}

Return:

{
  strengths: [],
  weaknesses: [],
  opportunities: [],
  threats: []
}
"""


def swot_task(payload):

    chain = ChatPromptTemplate.from_template(PROMPT) | llm

    response = chain.invoke({"payload": payload})

    return response.content
