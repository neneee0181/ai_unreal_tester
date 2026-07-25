"""LLM 프로바이더 공통 규약(추상) + 정규화 응답 타입.

핵심: 프로바이더마다 응답 모양 / 도구 포맷 / 메시지 히스토리 포맷이 다르다.
그 차이를 여기서 흡수해 루프가 '한 가지 모양'만 보게 한다.

- call() 은 원본 응답을 LLMResponse 로 정규화해 반환.
- 메시지 히스토리 포맷(어시스턴트 턴 / 도구결과)도 프로바이더가 다르므로
  append_assistant / append_tool_results 로 위임한다.
루프는 LLMResponse 와 이 두 메서드만 안다. 어떤 프로바이더인지는 모른다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    id: str          # 도구 호출 식별자 (결과를 되돌릴 때 짝맞춤용)
    name: str
    input: dict


@dataclass
class LLMResponse:
    text: str                    # 어시스턴트 텍스트 (여러 블록 합침)
    tool_calls: list             # list[ToolCall]
    stop_reason: str             # 정규화: "tool_use" | "end_turn"
    input_tokens: int
    output_tokens: int
    raw: dict = field(default_factory=dict)   # 원본 응답 (히스토리 append 에 씀)


class LLMProvider(ABC):
    """모든 LLM 프로바이더가 지켜야 할 공통 규약."""

    @abstractmethod
    def call(self, messages: list, tools: list) -> LLMResponse:
        """messages + (중립)도구스펙 을 보내고 LLMResponse 로 정규화해 반환."""
        raise NotImplementedError

    @abstractmethod
    def append_assistant(self, messages: list, response: LLMResponse) -> None:
        """어시스턴트 응답 턴을 messages 에 프로바이더 포맷으로 붙인다."""
        raise NotImplementedError

    @abstractmethod
    def append_tool_results(self, messages: list, results: list) -> None:
        """도구 결과를 messages 에 붙인다. results = list[(tool_call_id, output, is_error)]."""
        raise NotImplementedError
