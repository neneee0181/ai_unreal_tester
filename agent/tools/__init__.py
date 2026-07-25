"""tools — [손] 도구 계층 + 레지스트리.

레지스트리 역할:
  - specs()  : LLM 에 보낼 도구 스펙 목록 수집
  - execute(name, input) : 이름으로 도구 실행 + 예외 흡수
안다: 도구 공통 모양. 모른다: Claude, HTTP, 루프.

도구를 늘리려면: builtin/ 또는 game/ 에 Tool 만들고 아래 _REGISTRY 에 추가.
루프 코드는 안 고친다.
"""

from agent.tools.builtin.time_tool import get_time
from agent.tools.builtin.math_tool import add_numbers

# 이름 → Tool. 등록소.
_REGISTRY = {t.name: t for t in [get_time, add_numbers]}


def specs() -> list:
    """LLM(provider.call)에 넘길 도구 스펙 목록."""
    return [t.spec() for t in _REGISTRY.values()]


def execute(name: str, tool_input: dict) -> tuple[str, bool]:
    """도구 실행. (결과문자열, 에러여부) 반환.

    예외를 여기서 흡수해야 도구가 터져도 루프가 안 죽는다.
    게임 테스트는 액션 실패가 일상이라 필수.
    """
    tool = _REGISTRY.get(name)
    if tool is None:
        return f"에러: 알 수 없는 도구 '{name}'", True
    try:
        return str(tool.run(**tool_input)), False
    except Exception as error:
        return f"에러: {error}", True
