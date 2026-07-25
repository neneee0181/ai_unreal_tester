"""진행 이벤트 타입 (D13 — 출력 분리).

루프는 print 하지 않고, 사건이 생길 때마다 on_event(<이벤트>) 를 부른다.
누가 어떻게 출력하는지(CLI print / Electron JSON)는 이 파일이 모른다.
UI 는 isinstance 로 종류를 구분해 처리한다.
"""

from dataclasses import dataclass


@dataclass
class TurnStart:
    turn: int
    stop_reason: str | None


@dataclass
class AssistantText:
    # 도구 부르기 직전에 Claude 가 한 말
    text: str


@dataclass
class ToolCall:
    name: str
    input: dict


@dataclass
class ToolResult:
    name: str
    output: str
    is_error: bool


@dataclass
class FinalText:
    # 최종 답
    text: str


@dataclass
class LimitReached:
    max_turns: int


@dataclass
class Usage:
    # 누적 토큰
    input_tokens: int
    output_tokens: int
