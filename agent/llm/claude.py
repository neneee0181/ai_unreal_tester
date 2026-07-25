"""Anthropic Claude 프로바이더 — 생 HTTP 구현 (Phase 1 유일 구현).

역할: /v1/messages 로 requests POST, 응답 dict 반환.
안다: URL, 헤더(x-api-key / anthropic-version), max_tokens, 에러(예외로 올림).
모른다: 도구가 뭔지(그냥 받은 tools 전달), 루프가 있는지, 출력(print).
"""

import requests

from agent.llm.base import LLMProvider

API_URL = "https://api.anthropic.com/v1/messages"


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-haiku-4-5", max_tokens: int = 500):
        # 설정을 매개변수로 매번 넘기지 않고 객체가 들고 있는다.
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens

    def call(self, messages: list, tools: list) -> dict:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "tools": tools,        # ← 루프가 준 도구 목록을 그대로 전달
            "messages": messages,
        }

        response = requests.post(API_URL, headers=headers, json=body, timeout=60)

        # llm 계층은 print/exit 안 한다(경계). 에러는 예외로 올려 호출자가 처리.
        if response.status_code != 200:
            raise RuntimeError(f"Claude API {response.status_code}: {response.text}")

        return response.json()
