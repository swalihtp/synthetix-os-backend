from langchain_core.prompts import ChatPromptTemplate
from services.llm_service import llm

PROMPT = """
You are a market intelligence analyst.

Company Profile:

{company_profile}

Search Results:

{search_results}

Instructions:

Identify direct competitors.

Rules:

1. Prefer companies offering similar products/services.
2. Prefer competitors serving similar customers.
3. Rank by relevance.
4. Remove duplicates.

Return JSON.

[
  {
    "name": "",
    "website": "",
    "reason": ""
  }
]
"""


def competitor_discovery_task(payload):

    prompt = ChatPromptTemplate.from_template(PROMPT)

    chain = prompt | llm

    response = chain.invoke(
        {
            "company_profile": payload["company_profile"],
            "search_results": payload["search_results"],
        }
    )

    return response.content
