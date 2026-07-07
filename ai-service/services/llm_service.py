import os

from langchain_openai import ChatOpenAI

from services.env import get_openrouter_api_key

free_models = [
    'liquid/lfm-2.5-1.2b-thinking:free',
    'google/gemma-4-26b-a4b-it:free',
    'nvidia/nemotron-3-super-120b-a12b:free',
    'liquid/lfm-2.5-1.2b-instruct:free',
    'qwen/qwen3-next-80b-a3b-instruct:free',
    'nvidia/nemotron-nano-9b-v2:free',
    'openai/gpt-oss-20b:free',
    'cognitivecomputations/dolphin-mistral-24b-venice-edition:free'
]


llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "poolside/laguna-xs.2:free"),
    temperature=0,
    api_key=get_openrouter_api_key(),
    base_url="https://openrouter.ai/api/v1",
    timeout=180,
    max_retries=2,
)
