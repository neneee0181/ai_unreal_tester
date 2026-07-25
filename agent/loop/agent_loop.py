"""에이전트 루프 — Phase 1 핵심.

역할: messages 유지, LLM 호출, stop_reason 보고 도구 실행→결과 재주입 반복.
안다: messages, stop_reason, 턴 수, on_event 콜백.
모른다: HTTP/API키(llm 담당), print(ui 담당), datetime(도구 담당).
채우는 시점: Phase 1 리팩터 (loop.py 의 run() 을 print 걷어내고 이전).
"""
