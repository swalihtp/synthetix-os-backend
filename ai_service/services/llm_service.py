from langchain_openai import ChatOpenAI

from services.env import get_openrouter_api_key


llm = ChatOpenAI(
    model="google/gemma-4-26b-a4b-it:free",
    temperature=0,
    api_key=get_openrouter_api_key(),
    base_url="https://openrouter.ai/api/v1",
    timeout=180,
    max_retries=2,
)
