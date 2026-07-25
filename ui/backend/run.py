"""데스크탑 백엔드 진입점 — 개발 진입점 겸 Electron 이 spawn 할 대상.

역할:
  - 프로바이더를 고르고(get_provider), 루프(run)를 돌린다.
  - 실행: python -m ui.backend.run "질문"
현재 단계(리팩터 진행 중):
  - provider  → agent/llm 분리 완료.
  - 도구       → agent/tools 분리 완료 (specs/execute).
  - 남은 것: 루프(run)를 agent/loop/agent_loop.py 로 이동, print → on_event 로 교체(D13).
"""

import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from agent.llm import get_provider
from agent.tools import specs, execute

# .env 는 agent/ 안에 있다. 루트에서 python -m 으로 실행해도 찾도록 경로 명시.
#   ui/backend/run.py → parents[2] = 레포 루트
load_dotenv(Path(__file__).resolve().parents[2] / "agent" / ".env")

MAX_TURNS = 10   # 무한루프 방지 (크레딧 보호)


# ── 루프 : provider 와 도구 레지스트리를 쓴다 (구체 구현은 모름) ───────

def run(question: str, provider) -> None:
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": question},
    ]

    total_in = 0
    total_out = 0

    for turn in range(1, MAX_TURNS + 1):

        # ① LLM 호출 — 도구 스펙은 레지스트리에서
        data = provider.call(messages, specs())

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

        # ④ tool_use 블록 전부 실행 — 실행은 레지스트리에서
        results: list[dict[str, Any]] = []

        for block in data["content"]:
            if block.get("type") != "tool_use":
                continue

            name = block["name"]
            tool_input = block.get("input", {})
            print(f"  → 도구 호출: {name}({tool_input})")

            output, is_error = execute(name, tool_input)
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
