"""llm — [입] LLM 프로바이더 계층 + 팩토리.

get_provider(name): 이름으로 프로바이더 생성. UI(Electron)가 이 이름만 바꾸면 교체된다.
프로바이더는 응답을 LLMResponse 로 정규화하므로, 루프는 누구인지 몰라도 된다.
"""

import os

from agent.llm.base import LLMProvider
from agent.llm.claude import ClaudeProvider
from agent.llm.openai import OpenAIProvider
from agent.llm.deepseek import DeepSeekProvider

# 프로바이더 이름 → (환경변수 키, 생성함수)
_PROVIDERS = {
    "claude":   ("ANTHROPIC_API_KEY", lambda key: ClaudeProvider(key)),
    "openai":   ("OPENAI_API_KEY",    lambda key: OpenAIProvider(key)),
    "deepseek": ("DEEPSEEK_API_KEY",  lambda key: DeepSeekProvider(key)),
}


def available() -> list:
    """UI 드롭다운용 — 지원하는 프로바이더 이름 목록."""
    return list(_PROVIDERS.keys())


def get_provider(name: str) -> LLMProvider:
    """이름 → 프로바이더 객체. UI 프로바이더 선택의 열쇠."""
    entry = _PROVIDERS.get(name)
    if entry is None:
        raise ValueError(f"알 수 없는 프로바이더: {name} (가능: {available()})")

    env_key, factory = entry
    api_key = os.environ.get(env_key)
    if not api_key:
        raise RuntimeError(f"{env_key} 환경 변수가 없습니다.")
    return factory(api_key)
