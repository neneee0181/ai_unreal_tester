"""Anthropic Claude 프로바이더 — 생 HTTP 구현 (Phase 1 유일 구현).

역할: /v1/messages 로 requests POST, 응답 dict 반환.
안다: URL, 헤더(x-api-key / anthropic-version), max_tokens, 에러 처리.
모른다: 도구가 뭔지, 루프가 있는지, 출력(print).
채우는 시점: Phase 1 리팩터 (loop.py 의 call_claude 이전).
"""
