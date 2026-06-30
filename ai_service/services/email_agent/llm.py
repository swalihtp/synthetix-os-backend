from langchain_openai import ChatOpenAI

from services.env import get_openrouter_api_key

llm = ChatOpenAI(
    model="nvidia/nemotron-3-super-120b-a12b:free",
    temperature=0,
    api_key=get_openrouter_api_key(),
    base_url="https://openrouter.ai/api/v1",
)
