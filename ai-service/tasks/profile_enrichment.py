from langchain_core.prompts import ChatPromptTemplate
from services.llm_service import llm

PROMPT = """
You are a market intelligence analyst.

Current Company Profile:

{company_profile}

Detected Information Gaps:

{research_gaps}

Additional Research Results:

{additional_research}

Instructions:

1. Review the current company profile.
2. Review the newly collected research.
3. Fill missing information only if evidence exists.
4. Do not invent information.
5. Preserve existing fields.
6. Improve field accuracy if research provides better evidence.

Return a complete enriched company profile.

Return JSON only.

Expected structure:

{
  "industry": "",
  "subcategory": "",
  "business_model": "",
  "products": [],
  "services": [],
  "target_customers": [],
  "positioning": "",
  "value_proposition": "",
  "geographic_markets": [],
  "pricing_model": ""
}
"""


def profile_enrichment_task(payload):

    prompt = ChatPromptTemplate.from_template(PROMPT)

    chain = prompt | llm

    response = chain.invoke(
        {
            "company_profile": payload["company_profile"],
            "research_gaps": payload["research_gaps"],
            "additional_research": payload["additional_research"],
        }
    )

    return response.content
