---
memoc: true
type: core
scope: project-memory
created: 2026-07-27T04:19:12
updated: 2026-07-27T04:19:12
status: active
tags:
  - memoc
  - memoc/core
---
# Project Brief

This is the shortest project summary for a fresh agent. Keep it factual and easy to scan.

## Identity

<!-- memoc:identity:start -->
- Project name: `ai_unreal_tester`
- Detected stack: Not detected
<!-- memoc:identity:end -->

## Current Direction

학습 겸용 **언리얼 게임 테스트용 AI 에이전트**. 외부 Python 에이전트가 관찰(로그+스샷)→판단(LLM)→행동→검증 닫힌 루프로 게임 자율 테스트. 라이브러리 0개 자작으로 원리 학습 후 프레임워크(LangGraph/MCP/RAG) 레이어로 재구현=취업. 전체 플랜: `.memoc/wiki/project/plan.md` (v0.2.1).

진행 순서(사용자 결정): **#1 멀티프로바이더(완료) → #2 Electron MVP → #3 Phase 2 언리얼**. UI/UX는 병행하되 MVP만, 폼은 진짜 게임 데이터 위에서.

⚠️ `memoc update`는 이 섹션과 아래 Next Useful Work를 `_Not set yet._`으로 덮어씀. update 후 반드시 복구할 것(2회 발생).

## How To Approach

- Start from `session-summary.md`; search before opening more files.
- Open status, handoff, rules, map, project wiki, or knowledge wiki only when the task needs them.
- After durable work, update the smallest relevant memory set.
- Do not treat generated output folders as source unless the user explicitly asks.

## Next Useful Work

- #2 Electron MVP: `ui/backend/run.py`에 JSON 이벤트 출력 + stdin 질문 수신, `ui/desktop/*` 구현(spawn+IPC), 프로바이더 드롭다운(`available()`).

## Important Notes

_None yet._
