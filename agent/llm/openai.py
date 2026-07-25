"""OpenAI 호환 프로바이더 — 생 HTTP (/chat/completions).

OpenAI 와 DeepSeek 이 이 포맷을 공유하므로 여기 한 번 구현하고 DeepSeek 이 재사용.
Anthropic 과 다른 점:
- 인증: Authorization: Bearer
- 도구 스펙: {"type":"function","function":{name,description,parameters}}
- 응답: choices[0].message.content / .tool_calls (arguments 는 JSON 문자열)
- 멈춤: finish_reason ("tool_calls" -> tool_use, 그 외 -> end_turn)
- 히스토리: assistant 메시지 통째 / 도구결과 = role:"tool" 메시지 (tool_call_id 별로 하나씩)
"""

import json

import requests

from agent.llm.base import LLMProvider, LLMResponse, ToolCall


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini",
                 base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def call(self, messages: list, tools: list) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "content-type": "application/json",
        }
        body = {"model": self.model, "messages": messages}
        if tools:
            body["tools"] = [self._tool_spec(t) for t in tools]

        response = requests.post(
            f"{self.base_url}/chat/completions", headers=headers, json=body, timeout=60
        )
        if response.status_code != 200:
            raise RuntimeError(f"OpenAI-호환 API {response.status_code}: {response.text}")
        return self._to_response(response.json())

    @staticmethod
    def _tool_spec(neutral: dict) -> dict:
        # 중립 {name,description,input_schema} -> OpenAI function 포맷
        return {
            "type": "function",
            "function": {
                "name": neutral["name"],
                "description": neutral["description"],
                "parameters": neutral["input_schema"],
            },
        }

    def _to_response(self, raw: dict) -> LLMResponse:
        choice = raw.get("choices", [{}])[0]
        msg = choice.get("message", {})
        text = msg.get("content") or ""

        tool_calls = []
        for tc in msg.get("tool_calls", []) or []:
            fn = tc.get("function", {})
            args = fn.get("arguments") or "{}"
            try:
                parsed = json.loads(args)
            except json.JSONDecodeError:
                parsed = {}
            tool_calls.append(ToolCall(id=tc["id"], name=fn.get("name", ""), input=parsed))

        stop = "tool_use" if choice.get("finish_reason") == "tool_calls" else "end_turn"
        usage = raw.get("usage", {})
        return LLMResponse(
            text=text,
            tool_calls=tool_calls,
            stop_reason=stop,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            raw=raw,
        )

    def append_assistant(self, messages: list, response: LLMResponse) -> None:
        # OpenAI: 어시스턴트 메시지(tool_calls 포함) 통째로
        messages.append(response.raw["choices"][0]["message"])

    def append_tool_results(self, messages: list, results: list) -> None:
        # OpenAI: 도구결과는 tool_call_id 별로 role:"tool" 메시지 하나씩
        for tool_call_id, output, _is_error in results:
            messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": output})
