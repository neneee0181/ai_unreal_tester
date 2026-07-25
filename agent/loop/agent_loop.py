"""에이전트 루프 — Phase 1 핵심 (프로바이더 무관).

역할: messages 유지, provider 호출, stop_reason 보고 도구 실행→결과 재주입 반복.
안다: LLMResponse(정규화), provider.append_*, on_event 콜백, 도구 레지스트리.
모른다: HTTP/API키/응답모양(provider 담당), print(ui 담당), 도구 내부(tools 담당),
        메시지 히스토리 포맷(provider.append_* 가 담당).
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

        # ① LLM 호출 → 정규화된 응답 (누구인지 몰라도 된다)
        resp = provider.call(messages, specs())

        total_in += resp.input_tokens
        total_out += resp.output_tokens

        on_event(events.TurnStart(turn, resp.stop_reason))

        # ② 끝났으면 최종 텍스트 알리고 종료
        if resp.stop_reason != "tool_use":
            if resp.text:
                on_event(events.FinalText(resp.text))
            break

        # 도구 부르기 전에 뭔가 말했으면 알린다
        if resp.text:
            on_event(events.AssistantText(resp.text))

        # ③ 어시스턴트 턴 기록 (포맷은 provider 가 안다)
        provider.append_assistant(messages, resp)

        # ④ tool_call 전부 실행
        results: list = []   # list[(tool_call_id, output, is_error)]

        for tc in resp.tool_calls:
            on_event(events.ToolCall(tc.name, tc.input))

            output, is_error = execute(tc.name, tc.input)
            on_event(events.ToolResult(tc.name, output, is_error))

            results.append((tc.id, output, is_error))

        # ⑤ 도구 결과 되돌려주기 (포맷은 provider 가 안다)
        provider.append_tool_results(messages, results)

    else:
        on_event(events.LimitReached(MAX_TURNS))

    on_event(events.Usage(total_in, total_out))
