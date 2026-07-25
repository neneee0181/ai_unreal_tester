"""에이전트 루프 — Phase 1 핵심.

역할: messages 유지, provider 호출, stop_reason 보고 도구 실행→결과 재주입 반복.
안다: messages, stop_reason, 턴 수, on_event 콜백, 도구 레지스트리.
모른다: HTTP/API키(provider 담당), print(ui 담당), 도구 내부(tools 담당).
"""

from typing import Any, Callable

from agent.tools import specs, execute
from agent.loop import events

MAX_TURNS = 10   # 무한루프 방지 (크레딧 보호)


def run(question: str, provider, on_event: Callable) -> None:
    """관찰→판단→행동 루프. 출력은 안 한다 — on_event 로 사건만 알린다."""
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": question},
    ]

    total_in = 0
    total_out = 0

    for turn in range(1, MAX_TURNS + 1):

        # ① LLM 호출 (도구 스펙은 레지스트리에서)
        data = provider.call(messages, specs())

        usage = data.get("usage", {})
        total_in += usage.get("input_tokens", 0)
        total_out += usage.get("output_tokens", 0)

        stop_reason = data.get("stop_reason")
        on_event(events.TurnStart(turn, stop_reason))

        # ② 끝났으면 최종 텍스트 알리고 종료
        if stop_reason != "tool_use":
            for block in data.get("content", []):
                if block.get("type") == "text":
                    on_event(events.FinalText(block.get("text", "")))
            break

        # 도구 부르기 전에 뭔가 말했으면 알린다
        for block in data.get("content", []):
            if block.get("type") == "text":
                on_event(events.AssistantText(block.get("text", "")))

        # ③ assistant 턴을 통째로 기록  ★ 이걸 빼면 400 에러
        messages.append({"role": "assistant", "content": data["content"]})

        # ④ tool_use 블록 전부 실행
        results: list[dict[str, Any]] = []

        for block in data["content"]:
            if block.get("type") != "tool_use":
                continue

            name = block["name"]
            tool_input = block.get("input", {})
            on_event(events.ToolCall(name, tool_input))

            output, is_error = execute(name, tool_input)
            on_event(events.ToolResult(name, output, is_error))

            result_block = {
                "type": "tool_result",
                "tool_use_id": block["id"],
                "content": output,
            }
            if is_error:
                result_block["is_error"] = True

            results.append(result_block)

        # ⑤ 결과 전부를 한 개의 user 메시지로 되돌려준다
        messages.append({"role": "user", "content": results})

    else:
        on_event(events.LimitReached(MAX_TURNS))

    on_event(events.Usage(total_in, total_out))
