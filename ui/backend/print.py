"""출력 포맷터 — 이벤트를 "어떻게 보여줄지"만 담당 (D13).

run.py 는 조립만 하고, "이벤트 → 글자/JSON" 변환은 여기로 분리.
두 포맷터:
  - cli_print  : 사람이 터미널에서 보기 좋게
  - json_print : Electron 이 읽는 기계용 JSON 한 줄

주의: 모듈명이 print.py 지만, 파일 안에서 쓰는 print(...) 는 파이썬 내장 그대로다.
      import 은 항상 루트 절대경로: `from ui.backend.print import json_print`.
"""

import json
from dataclasses import asdict

from agent.loop import events


def cli_print(event) -> None:
    """이벤트 → 터미널 출력. (개발 중 눈으로 확인용)"""
    if isinstance(event, events.TurnStart):
        print(f"\n[턴 {event.turn}] stop_reason={event.stop_reason}")
    elif isinstance(event, events.AssistantText):
        print(f"  (LLM) {event.text}")
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


def json_print(event) -> None:
    """이벤트(dataclass) → JSON 한 줄로 stdout 에 찍는다.

    - type   : 이벤트 종류 이름(클래스명). 화면(React)이 이걸로 분기한다.
    - 나머지 : dataclass 필드들(asdict 로 dict 변환).
    예) {"type": "ToolCall", "name": "get_time", "input": {}}
    'JSON Lines' 규약: 한 줄 = 이벤트 하나. Electron 이 줄 단위로 읽기 쉽다.
    """
    payload = {"type": type(event).__name__, **asdict(event)}
    # flush=True : 버퍼에 안 쌓고 즉시 내보내야 Electron 이 실시간으로 받는다.
    print(json.dumps(payload, ensure_ascii=False), flush=True)
