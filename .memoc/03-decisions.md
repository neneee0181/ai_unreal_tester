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
- **D4** ~~LLM = Claude 단일~~ → **개정(2026-07-25)**: 멀티프로바이더(Claude/OpenAI/DeepSeek), API 키 + dotenv. 구독 호출은 비공식이라 배제. OpenAI·DeepSeek은 API 모양 동일, Claude만 독자 → `agent/llm/base.py`에서 `LLMResponse`로 정규화.
- **D5** 라이브러리 0개 자작 (생 HTTP + 생 소켓 + JSON). SDK/공식MCP/LangChain 초반 미사용 — 원리 학습 목적.
- **D6** 통제 = Tool Use 직접 구현 (tool_use/tool_result 루프).
- **D7** 브릿지 프로토콜: 자체 JSON 먼저 → 나중에 진짜 MCP(JSON-RPC) 재구현.
- **D8** 고수준 액션 우선 + 엔진 assertion. LLM에 성공판정 안 시킴.
- **D9** ~~CLI → Streamlit → 최후 Electron~~ → **개정(2026-07-25)**: UI = Electron 데스크탑 확정. Python 뇌와 프로세스 분리, stdio JSON 통신. JS↔Py 직접 import 불가라 `ui/backend/run.py`를 spawn. 뼈대는 지금, 구현은 #2.
- **D10** 언리얼 5.8 대상. 공식 MCP 존재하나 학습 목적으로 재사용 안 함.
- 프레임워크(LangGraph/MCP/RAG/CrewAI/평가·관측/배포)는 자작 코어 위 리팩터링 레이어로 나중에 얹음(취업 경쟁력).

2026-07-25 — 구조/실행 규약 (plan v0.2.x)

- **D11** 미래 구조 선반영(빈 폴더 미리 생성). "이 파일 어디 두지" 고민 제거.
- **D12** 실행은 레포 루트에서 `python -m ui.backend.run`. 모든 패키지에 `__init__.py`, import는 루트 절대경로(상대 import 금지).
- **D13** 출력은 이벤트 콜백(`on_event`)으로 루프 밖에 위임. 루프 안 `print` 금지 → UI 갈아끼워도 루프 무수정.
- **D14** 언리얼 프로젝트 폴더 = `ai_agent_test/` (레포 루트 바로 밑), 플러그인은 그 아래. Phase 2에서 언리얼 에디터가 생성.

2026-07-27 — 진행 순서

- 사용자 결정: **#1 멀티프로바이더(완료) → #2 Electron MVP → #3 Phase 2 언리얼**.
