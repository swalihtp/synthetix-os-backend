from langchain_core.prompts import ChatPromptTemplate

from services.llm_service import llm

PROMPT = """
Analyze company information.

Payload:

{payload}

Determine:

1. Industry
2. Subcategory
3. Products
4. Services
5. Target Customers
6. Positioning
7. Business Model

Return JSON.
"""


def company_profile_task(payload):

    prompt = ChatPromptTemplate.from_template(PROMPT)

    chain = prompt | llm

    response = chain.invoke({"payload": payload})

    return response.content
