"""데스크탑 백엔드 진입점 — 개발 진입점 겸 Electron 이 spawn 할 대상.

역할(얇음):
  - 프로바이더 선택(get_provider)
  - 루프(agent_loop.run) 호출
  - on_event 로 들어온 사건을 화면에 출력 (여기 cli_print 담당)
실행: python -m ui.backend.run "질문"

Electron 붙일 때: cli_print 를 'JSON 을 stdout 에 찍는 함수' 로만 바꾸면 됨.
루프는 손 안 댄다 (D13).
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from agent.llm import get_provider
from agent.loop.agent_loop import run
from agent.loop import events

# .env 는 agent/ 안. 루트에서 python -m 으로 실행해도 찾도록 경로 명시.
load_dotenv(Path(__file__).resolve().parents[2] / "agent" / ".env")


def cli_print(event) -> None:
    """이벤트 → 터미널 출력. (Electron 은 이 함수만 JSON 버전으로 교체)"""
    if isinstance(event, events.TurnStart):
        print(f"\n[턴 {event.turn}] stop_reason={event.stop_reason}")
    elif isinstance(event, events.AssistantText):
        print(f"  (Claude) {event.text}")
    elif isinstance(event, events.ToolCall):
        print(f"  → 도구 호출: {event.name}({event.input})")
    elif isinstance(event, events.ToolResult):
        print(f"  ← 결과: {event.output}")
    elif isinstance(event, events.FinalText):
        print(event.text)
    elif isinstance(event, events.LimitReached):
        print(f"\n턴 한도({event.max_turns}) 초과. 중단.")
    elif isinstance(event, events.Usage):
        print(f"\n=== 누적 토큰 : 입력 {event.input_tokens} / 출력 {event.output_tokens} ===")


def main() -> None:
    if len(sys.argv) < 2:
        print('사용법 : python -m ui.backend.run "claude에게 보낼 질문"')
        sys.exit(1)

    # 프로바이더 이름 — 나중에 Electron 이 이 값을 보낸다.
    # 개발 중엔 LLM_PROVIDER 환경변수로 전환: claude(기본) / openai / deepseek
    name = os.environ.get("LLM_PROVIDER", "claude")
    provider = get_provider(name)

    run(" ".join(sys.argv[1:]), provider, on_event=cli_print)


if __name__ == "__main__":
    main()
