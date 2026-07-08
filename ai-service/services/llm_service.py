from langchain_openai import ChatOpenAI

from services.env import get_openrouter_api_key,get_model
import os
from dotenv import load_dotenv

FREE_MODELS = [
    'tencent/hy3:free',
    'poolside/laguna-xs-2.1:free'
]

load_dotenv()

llm = ChatOpenAI(
    model=get_model(),
    temperature=0,
    api_key=get_openrouter_api_key(),
    base_url="https://openrouter.ai/api/v1",
    timeout=180,
    max_retries=2,
)
