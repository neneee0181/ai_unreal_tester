"""add_numbers 도구 — 두 수의 합 반환 (Phase 1 학습용, 병렬 도구 호출 확인용).

안다: 산수. 모른다: Claude, 루프.
"""

from agent.tools.base import Tool


def _add_numbers(a, b, **kwargs) -> str:
    return str(a + b)


add_numbers = Tool(
    name="add_numbers",
    description="두 숫자를 더한 결과를 문자열로 반환한다. 사용자가 두 수의 합을 물으면 사용.",
    input_schema={
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "첫 번째 숫자"},
            "b": {"type": "number", "description": "두 번째 숫자"},
        },
        "required": ["a", "b"],
    },
    run=_add_numbers,
)
