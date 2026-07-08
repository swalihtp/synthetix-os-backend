from langchain_core.prompts import ChatPromptTemplate
from services.llm_service import llm

PROMPT = """
Create executive summary.

Payload:

{payload}

Maximum 500 words.
"""


def executive_summary_task(payload):

    chain = ChatPromptTemplate.from_template(PROMPT) | llm

    response = chain.invoke({"payload": payload})

    return response.content
