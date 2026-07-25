"""get_time 도구 — 현재 시각 반환 (Phase 1 학습용).

안다: datetime. 모른다: Claude, 루프.
"""

from datetime import datetime

from agent.tools.base import Tool


def _get_time(**kwargs) -> str:
    return datetime.now().isoformat(timespec="seconds")


get_time = Tool(
    name="get_time",
    description="현재 시각을 ISO 형식 문자열로 반환한다. 사용자가 시간이나 날짜를 물으면 사용.",
    input_schema={"type": "object", "properties": {}, "required": []},
    run=_get_time,
)
