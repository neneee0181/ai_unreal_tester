"""도구 공통 규약(Tool).

역할: name / description / input_schema / run 을 한 덩어리로 묶는다.
주의: description 은 Claude 가 '언제 쓸지' 판단하는 유일한 근거.
모른다: 특정 도구의 실제 동작(각 도구 모듈이 채움), Claude, 루프.
"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    run: Callable[..., str]   # **input -> str

    def spec(self) -> dict:
        """LLM 에 보낼 스펙(JSON schema). run 은 뺀다 — LLM 은 실행함수를 모른다."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
