---
memoc: true
type: core
scope: project-memory
created: 2026-07-23T10:38:37
updated: 2026-07-23T10:38:37
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

학습 겸용 **언리얼 게임 테스트용 AI 에이전트** 개발. 외부 Python 에이전트가 언리얼 C++ 브릿지를 통해 관찰(로그+스크린샷)→판단(Claude)→행동(입력/명령)→검증(엔진 assertion) 닫힌 루프로 게임을 자율 테스트. 라이브러리 0개 자작으로 원리 학습 후 프레임워크(LangGraph/MCP/RAG) 레이어로 재구현 = 취업 경쟁력. 전체 플랜: `.memoc/wiki/project/plan.md` (v0.1.0).

## How To Approach

- Start from `session-summary.md`; search before opening more files.
- Open status, handoff, rules, map, project wiki, or knowledge wiki only when the task needs them.
- After durable work, update the smallest relevant memory set.
- Do not treat generated output folders as source unless the user explicitly asks.

## Next Useful Work

- Phase 0: 생 HTTP로 Claude API 호출 (curl → Python `requests`). `wiki/project/plan.md` Part 1 참고.

## Important Notes

_None yet._
