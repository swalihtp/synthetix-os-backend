from langchain_core.prompts import ChatPromptTemplate
from services.llm_service import llm

PROMPT = """
Generate complete Market Intelligence Report.

Payload:

{payload}

Include:

1 Executive Summary
2 Company Profile
3 Competitor Analysis
4 Industry Trends
5 SWOT
6 Recommendations

Return markdown.
"""


def market_report_task(payload):

    chain = ChatPromptTemplate.from_template(PROMPT) | llm

    response = chain.invoke({"payload": payload})

    return response.content
