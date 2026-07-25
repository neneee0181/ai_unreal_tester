"""DeepSeek 프로바이더 — OpenAI 호환. openai.py 재사용, URL/모델만 다름."""

from agent.llm.openai import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__(api_key, model=model, base_url="https://api.deepseek.com/v1")
