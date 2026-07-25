"""LLM 프로바이더 공통 규약(추상).

역할: call(messages, tools) -> dict 인터페이스 정의. 모든 프로바이더가 이 모양을 지킨다.
안다: '메시지+도구 받아 응답 dict 반환'이라는 계약.
모른다: Anthropic/OpenAI 등 구체 구현, 루프, 도구 내용.
채우는 시점: Phase 1 (claude.py 뽑을 때 같이).
"""
