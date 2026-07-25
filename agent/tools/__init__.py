"""tools — [손] 도구 계층 + 레지스트리.

레지스트리 역할: 도구 스펙 수집(specs) + 이름→실행(run) + 예외 흡수.
안다: 도구 공통 모양. 모른다: Claude, HTTP.
채우는 시점: Phase 1 (loop.py 의 execute_tool / TOOLS 를 여기로).
"""
