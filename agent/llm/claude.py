"""Anthropic Claude 프로바이더 — 생 HTTP (Anthropic 포맷).

- 도구 스펙: 중립 {name,description,input_schema} 를 그대로 씀 (Anthropic 이 이 모양).
- 응답: content 블록 배열 → LLMResponse 로 정규화.
- 히스토리: assistant 턴 = content 블록 통째 / 도구결과 = user 메시지 안 tool_result 블록.
"""

import requests

from agent.llm.base import LLMProvider, LLMResponse, ToolCall

API_URL = "https://api.anthropic.com/v1/messages"


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-haiku-4-5", max_tokens: int = 500):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens

    def call(self, messages: list, tools: list) -> LLMResponse:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "tools": tools,             # 중립 스펙 그대로
            "messages": messages,
        }
        response = requests.post(API_URL, headers=headers, json=body, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"Claude API {response.status_code}: {response.text}")
        return self._to_response(response.json())

    def _to_response(self, raw: dict) -> LLMResponse:
        text = "".join(
            b.get("text", "") for b in raw.get("content", []) if b.get("type") == "text"
        )
        tool_calls = [
            ToolCall(id=b["id"], name=b["name"], input=b.get("input", {}))
            for b in raw.get("content", [])
            if b.get("type") == "tool_use"
        ]
        stop = "tool_use" if raw.get("stop_reason") == "tool_use" else "end_turn"
        usage = raw.get("usage", {})
        return LLMResponse(
            text=text,
            tool_calls=tool_calls,
            stop_reason=stop,
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            raw=raw,
        )

    def append_assistant(self, messages: list, response: LLMResponse) -> None:
        # Anthropic: 어시스턴트 턴 = 원본 content 블록 통째 (★ 빼면 400)
        messages.append({"role": "assistant", "content": response.raw["content"]})

    def append_tool_results(self, messages: list, results: list) -> None:
        # Anthropic: 도구결과 = user 메시지 하나 안에 tool_result 블록들
        content = []
        for tool_call_id, output, is_error in results:
            block = {"type": "tool_result", "tool_use_id": tool_call_id, "content": output}
            if is_error:
                block["is_error"] = True
            content.append(block)
        messages.append({"role": "user", "content": content})
