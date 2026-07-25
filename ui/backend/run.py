"""데스크탑 백엔드 진입점 — Electron 이 spawn 해서 표준입출력으로 통신.

역할:
  - agent/loop 를 실행하고, on_event 콜백을 stdout JSON 라인으로 흘린다.
  - stdin 으로 사용자 질문 / 명령을 받는다.
안다: loop 호출, 이벤트 → JSON 직렬화.
모른다: 화면 렌더링(그건 Electron renderer 몫), HTTP(그건 agent/llm 몫).
왜 여기: 루프는 순수(on_event 만) 유지, 이 파일이 'JSON stdout' UI 어댑터 역할.
실행:
  - 개발 중 단독: python -m ui.backend.run   (터미널에서 JSON 이벤트 눈으로)
  - 실제: Electron main/agent-process.js 가 이 모듈을 spawn.
채우는 시점: 데스크탑 붙일 때 (Phase 1 후반~). 지금은 자리만.
"""
