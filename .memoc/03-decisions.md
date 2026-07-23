---
memoc: true
type: state
scope: project-memory
created: 2026-07-23T10:38:31
updated: 2026-07-23T10:38:31
status: active
tags:
  - memoc
  - memoc/state
---
# Decisions

Durable project decisions live here. Keep entries short, dated, and useful to future agents.

## Decision Log

2026-07-23 — 초기 아키텍처 확정 (전체: `.memoc/wiki/project/plan.md` v0.1.0)

- **D1** 외부 에이전트 (게임 밖). 게임 크래시해도 테스터 살아야 함(크래시도 버그).
- **D2** 에이전트 = Python 3.12+.
- **D3** 브릿지 = 언리얼 C++ 플러그인 (판단 안 함, 상태/입력/판정만).
- **D4** LLM = Claude console API 키. 구독 계정 호출은 비공식/불안정이라 배제.
- **D5** 라이브러리 0개 자작 (생 HTTP + 생 소켓 + JSON). SDK/공식MCP/LangChain 초반 미사용 — 원리 학습 목적.
- **D6** 통제 = Tool Use 직접 구현 (tool_use/tool_result 루프).
- **D7** 브릿지 프로토콜: 자체 JSON 먼저 → 나중에 진짜 MCP(JSON-RPC) 재구현.
- **D8** 고수준 액션 우선 + 엔진 assertion. LLM에 성공판정 안 시킴.
- **D9** UI: CLI → Streamlit → (최후) Tauri/Electron. Electron 지금 안 씀(Python 에이전트라 혼용 삽질).
- **D10** 언리얼 5.8 대상. 공식 MCP 존재하나 학습 목적으로 재사용 안 함.
- 프레임워크(LangGraph/MCP/RAG/CrewAI/평가·관측/배포)는 자작 코어 위 리팩터링 레이어로 나중에 얹음(취업 경쟁력).
