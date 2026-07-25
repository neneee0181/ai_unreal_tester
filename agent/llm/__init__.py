"""llm — [입] LLM 프로바이더 계층 + 팩토리.

get_provider(name): 이름으로 프로바이더 생성. UI(Electron)가 이 이름만 바꾸면 교체된다.
도구/루프를 모른다.
"""

import os

from agent.llm.base import LLMProvider
from agent.llm.claude import ClaudeProvider


def get_provider(name: str) -> LLMProvider:
    """이름 → 프로바이더 객체. UI 프로바이더 선택의 열쇠."""
    if name == "claude":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY 환경 변수가 없습니다.")
        return ClaudeProvider(api_key=api_key)

    # if name == "openai":   return OpenAIProvider(...)    ← 나중
    # if name == "deepseek": return DeepSeekProvider(...)  ← 나중

    raise ValueError(f"알 수 없는 프로바이더: {name}")
