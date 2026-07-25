"""데스크탑 백엔드 진입점 — 개발 진입점 겸 Electron 이 spawn 할 대상.

역할:
  - 프로바이더를 고르고(get_provider), 루프(run)를 돌린다.
  - 실행: python -m ui.backend.run "질문"
현재 단계(리팩터 진행 중):
  - provider 는 agent/llm 으로 분리 완료.
  - 도구(TOOLS/execute_tool)와 루프(run)는 아직 여기 임시로 있음 → 다음 스텝에서
    agent/tools/ 와 agent/loop/agent_loop.py 로 이동, print 는 on_event 로 교체(D13).
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from agent.llm import get_provider

# .env 는 agent/ 안에 있다. 루트에서 python -m 으로 실행해도 찾도록 경로 명시.
#   ui/backend/run.py → parents[2] = 레포 루트
load_dotenv(Path(__file__).resolve().parents[2] / "agent" / ".env")

MAX_TURNS = 10   # 무한루프 방지 (크레딧 보호)


# ── [임시] 도구 : 다음 스텝에서 agent/tools/ 로 이동 ──────────────────
TOOLS = [
    {
        "name": "get_time",
        "description": "현재 시각을 ISO 형식 문자열로 반환한다. 사용자가 시간이나 날짜를 물으면 사용.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "add_numbers",
        "description": "두 숫자를 더한 결과를 문자열로 반환한다. 사용자가 두 수의 합을 물으면 사용.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "첫 번째 숫자"},
                "b": {"type": "number", "description": "두 번째 숫자"},
            },
            "required": ["a", "b"],
        },
    },
]


def get_time(**kwargs) -> str:
    return datetime.now().isoformat(timespec="seconds")


def add_numbers(a, b, **kwargs) -> str:
    return str(a + b)


TOOL_FUNCS = {"get_time": get_time, "add_numbers": add_numbers}


def execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """도구 실행. (결과문자열, 에러여부) 반환. 예외를 흡수해 루프가 안 죽게 한다."""
    func = TOOL_FUNCS.get(name)
    if func is None:
        return f"에러: 알 수 없는 도구 '{name}'", True
    try:
        return str(func(**tool_input)), False
    except Exception as error:
        return f"에러: {error}", True


# ── 루프 : provider 를 받아서 쓴다 (Claude 인지 모름) ─────────────────

def run(question: str, provider) -> None:
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": question},
    ]

    total_in = 0
    total_out = 0

    for turn in range(1, MAX_TURNS + 1):

        # ① LLM 호출 — call_claude 대신 provider.call
        data = provider.call(messages, TOOLS)

        usage = data.get("usage", {})
        total_in += usage.get("input_tokens", 0)
        total_out += usage.get("output_tokens", 0)

        stop_reason = data.get("stop_reason")
        print(f"\n[턴 {turn}] stop_reason={stop_reason}")

        # ② 끝났으면 텍스트 출력하고 종료
        if stop_reason != "tool_use":
            for block in data.get("content", []):
                if block.get("type") == "text":
                    print(block.get("text", ""))
            break

        # 도구 부르기 전에 뭔가 말했으면 같이 보여준다
        for block in data.get("content", []):
            if block.get("type") == "text":
                print(f"  (Claude) {block.get('text', '')}")

        # ③ assistant 턴을 통째로 기록  ★ 이걸 빼면 400 에러
        messages.append({"role": "assistant", "content": data["content"]})

        # ④ tool_use 블록 전부 실행
        results: list[dict[str, Any]] = []

        for block in data["content"]:
            if block.get("type") != "tool_use":
                continue

            name = block["name"]
            tool_input = block.get("input", {})
            print(f"  → 도구 호출: {name}({tool_input})")

            output, is_error = execute_tool(name, tool_input)
            print(f"  ← 결과: {output}")

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
        print(f"\n턴 한도({MAX_TURNS}) 초과. 중단.")

    print(f"\n=== 누적 토큰 : 입력 {total_in} / 출력 {total_out} ===")


def main() -> None:
    if len(sys.argv) < 2:
        print('사용법 : python -m ui.backend.run "claude에게 보낼 질문"')
        sys.exit(1)

    # 프로바이더 이름 — 나중에 Electron 이 이 값을 보낸다.
    provider = get_provider("claude")

    run(" ".join(sys.argv[1:]), provider)


if __name__ == "__main__":
    main()
