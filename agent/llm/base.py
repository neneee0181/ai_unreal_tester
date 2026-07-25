"""LLM 프로바이더 공통 규약(추상).

역할: call(messages, tools) -> dict 인터페이스 정의. 모든 프로바이더가 이 모양을 지킨다.
안다: '메시지+도구 받아 응답 dict 반환'이라는 계약.
모른다: Anthropic/OpenAI 등 구체 구현, 루프, 도구 내용.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """모든 LLM 프로바이더가 지켜야 할 공통 규약."""

    @abstractmethod
    def call(self, messages: list, tools: list) -> dict:
        """messages + tools 를 보내고 응답 dict 를 반환한다.

        루프는 이 메서드만 안다. 어떤 프로바이더인지는 모른다.
        """
        raise NotImplementedError
