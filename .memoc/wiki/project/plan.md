---
memoc: true
type: wiki
scope: project-memory
version: 0.1.0
created: 2026-07-23
updated: 2026-07-23
status: active
confidence: high
tags:
  - memoc
  - memoc/wiki
  - memoc/project-wiki
  - plan
  - unreal
  - ai-agent
  - memoc/project-doc
---
# AI Unreal Tester — 개발 플랜

> Version 0.1.0 · 2026-07-23

## 최종 목표

**학습과 함께 만드는, 언리얼 게임 테스트용 AI 에이전트.**

- 코드가 남긴 로그/상태를 기반으로 AI가 게임을 스스로 플레이하며 테스트
- 사용자가 키맵·승리조건·테스트목표를 입력하면 AI가 그걸 보고 판단
- 관찰(로그+스크린샷) → 판단(LLM) → 행동(입력/명령) → 검증(엔진 판정)의 닫힌 루프
- 부가 목표: AI 에이전트 개발 핵심 기술을 바닥부터 직접 구현하며 공부 + 취업 경쟁력

## 핵심 원칙

1. **자작 우선**: 라이브러리/프레임워크 0개로 원리부터. SDK, 공식 MCP, LangChain 안 씀(초반).
2. **자작 후 프레임워크**: 원리 이해한 뒤 같은 프로젝트를 프레임워크로 재구현 = 깊이 + 취업.
3. **스코프 고정**: 게임 테스트 특화. 범용 Codex 클론으로 번지지 않기.
4. **작게 쌓기**: 각 Phase = 명확한 배움 한 조각 + 완료 기준.

---

## 확정된 결정 (Decisions)


| #   | 결정                                        | 이유                                          |
| --- | ----------------------------------------- | ------------------------------------------- |
| D1  | 외부 에이전트 (게임 밖)                            | 게임 크래시해도 테스터 살아야 함. 크래시도 버그.                |
| D2  | 에이전트 = Python 3.12+                       | LLM 생태계, 빠른 반복, 학습 쉬움                       |
| D3  | 브릿지 = 언리얼 C++ 플러그인                        | 판단 안 함. 상태 노출 + 입력 + 판정만                    |
| D4  | LLM = Claude API (console API 키)          | 구독 계정 호출은 비공식/불안정 → API 키 추천                |
| D5  | 라이브러리 0개 자작                               | 생 HTTP + 생 소켓 + JSON. SDK/공식MCP/LangChain X |
| D6  | 통제 패턴 = Tool Use 직접 구현                    | tool_use/tool_result 루프 = 에이전트 심장           |
| D7  | 브릿지 프로토콜: 자체 JSON → 나중에 진짜 MCP            | A→B 학습 사다리                                  |
| D8  | 고수준 액션 우선 + 엔진 assertion                  | LLM에 성공판정 시키지 마. 엔진이 `boss.hp==0` 판정        |
| D9  | UI: CLI → Streamlit → (최후) Tauri/Electron | Electron 지금 X. Python 에이전트라 섞으면 삽질          |
| D10 | 언리얼 최신(5.8) 대상                            | 공식 MCP 존재하나 재사용 안 함(자작 학습 목적)               |


---

## 아키텍처

```
┌─ 에이전트 (Python, 100% 자작) ──────────────────────┐
│  llm_client.py   ← 생 HTTP, Claude API 직접 호출     │
│  tools.py        ← 도구 JSON schema 정의             │
│  agent_loop.py   ← tool_use/tool_result 루프 직접    │
│  bridge_client.py← 언리얼로 명령 (자체 프로토콜)      │
│  knowledge/, scenarios/, reports/                    │
│  (UI: CLI → Streamlit)                               │
└──────────────────┬───────────────────────────────── ┘
                   │ 자체 JSON 프로토콜 → (나중) MCP
┌──────────────────┴──── 언리얼 5.8 (C++ 자작) ─────── ┐
│  AITesterBridge 플러그인                             │
│   · 소켓/HTTP 서버 (직접)                            │
│   · GetGameState()      · CaptureView()              │
│   · PerformAction()     · EvaluateAssertions()       │
│   · PressInput()        · ResetScenario(seed)        │
└───────────────────────────────────────────────────── ┘
```

### 폴더 구조

```
ai_unreal_tester/
├── agent/
│   ├── llm_client.py       # 생 HTTP LLM 호출
│   ├── tools.py            # 도구 스키마
│   ├── agent_loop.py       # tool use 루프
│   ├── bridge_client.py    # 언리얼 통신
│   ├── ui/                 # Streamlit 대시보드 (나중)
│   ├── knowledge/          # keymap.yaml, goals.yaml
│   ├── scenarios/
│   └── reports/
└── UnrealPlugin/
    └── AITesterBridge/     # C++
```

---

## Tool Use — 직접 구현할 메커니즘 (참고)

```
1. POST https://api.anthropic.com/v1/messages
   헤더: x-api-key, anthropic-version
   바디: {model, max_tokens, messages:[...], tools:[...]}  # tools = 자작 JSON schema
2. 응답: stop_reason=="tool_use" → content에 {type:"tool_use", id, name, input}
3. 그 도구 실행 (브릿지로 언리얼 전달)
4. 결과 재주입: {role:"user", content:[{type:"tool_result", tool_use_id, content}]}
5. stop_reason=="end_turn" 까지 루프
```

---

## Part 1 — 자작 코어 Phase (원리 학습)


| Phase  | 목표                           | 배움                      | 완료 기준                     |
| ------ | ---------------------------- | ----------------------- | ------------------------- |
| **0**  | 생 HTTP로 Claude API 호출        | API 인증, 메시지 포맷          | 터미널에서 Claude 답 받음         |
| **1**  | Tool Use 루프 (가짜 로컬 도구로)      | 에이전트 심장, tool use 완전 이해 | Claude가 도구 부르고 결과 받아 최종답  |
| **2**  | 언리얼 플러그인 뼈대 + 소켓             | 플러그인 구조, C++ 네트워킹       | Python↔언리얼 ping/pong      |
| **3**  | `GetGameState` 도구            | 게임 상태 접근, 직렬화           | Python이 실시간 게임 상태 봄       |
| **4**  | `PerformAction` (고수준 먼저)     | 언리얼 입력/액션 시스템           | Python 명령으로 캐릭터 이동        |
| **5**  | 통합: LLM이 게임 조종               | 관찰→판단→행동 닫힌 루프          | 자연어 목표로 자율 플레이            |
| **6**  | `EvaluateAssertions` (엔진 판정) | 검증 가능한 테스트 설계           | pass/fail 객관 판정           |
| **7**  | 스크린샷 + 비전                    | 멀티모달 메시지 포맷, 비용 최적화     | 렌더/UI 버그 감지               |
| **8**  | 지식베이스 + 시나리오 (YAML)          | 프롬프트/컨텍스트 설계            | YAML만 고쳐 새 테스트 추가         |
| **9**  | 결정성 + 리포트                    | 재현성, 자동 리포팅             | 시나리오 배치→리포트 자동생성          |
| **10** | 자체 프로토콜 → 진짜 MCP 재구현         | MCP 스펙(JSON-RPC) 내재화    | 표준 MCP 클라(Claude Code) 붙음 |


### 상태 JSON 예시

```json
{
  "time": 18.42, "scenario": "tutorial_boss",
  "player": {"hp": 72, "location": [120.4,-88.2,30.0], "is_stuck": false},
  "objective": {"id": "kill_boss", "status": "active"},
  "visible_enemies": [{"id": "boss_01", "hp": 340, "distance": 620}],
  "recent_events": [{"type": "damage_received", "amount": 12}]
}
```

### 행동 예시 (고수준 우선)

```json
{"action": "move_to", "target": [100,300,0], "timeout": 5}
{"action": "input", "key": "SpaceBar", "duration": 0.1}
```

---

## Part 2 — 프레임워크 레이어 (취업 경쟁력)

자작 코어 위에 **리팩터링 레이어**로 얹음. 새 프로젝트 아님. 같은 테스터를 프레임워크로 재구현 = 비교학습.


| Layer  | 기술                                   | 전제       | 배움               | 시장가치     |
| ------ | ------------------------------------ | -------- | ---------------- | -------- |
| **L1** | **LangGraph**로 에이전트 루프 재구현           | Phase 5  | 상태그래프, 자작 루프와 비교 | ★ 최고연봉   |
| **L2** | **MCP** 표준화                          | Phase 10 | JSON-RPC MCP 스펙  | ★ 수요급상승  |
| **L3** | **RAG + 벡터DB**(Chroma) 지식 강화         | Phase 8  | 임베딩, 벡터검색, RAG   | 거의 모든 공고 |
| **L4** | **멀티에이전트**(CrewAI/LangGraph)         | L1       | 역할설계, 오케스트레이션    | 스택 따라    |
| **L5** | **평가+관측**(LangSmith/Langfuse, RAGAS) | L1       | LLMOps, eval, 추적 | 시니어 구분점  |
| **L6** | **배포**(FastAPI + Docker)             | L1       | 서비스화, LLMOps     | 기본       |
| **L7** | **프롬프트 인젝션 방어**                      | L3       | 에이전트 보안          | 차별점      |


### 멀티에이전트 역할 (L4 예시)

- **탐험가**: 맵 훑기 / **공격수**: 전투 테스트 / **판정관**: 버그 판정

---

## 기술 용어집 (참고)

- **LangChain**: LLM 앱 조립 툴킷. 이제 기본기(구인 34%).
- **LangGraph**: 에이전트를 그래프(노드+엣지)로. 상태유지/분기/루프. 프로덕션 지배, 최고연봉.
- **CrewAI**: 역할기반 멀티에이전트. / **AutoGen**: 대화형 멀티에이전트(MS).
- **LlamaIndex**: RAG 특화. / **RAG**: 외부 문서 찾아 LLM에 넣어 정확도↑.
- **벡터DB**: 임베딩 저장/검색(Chroma, pgvector, Qdrant). **리랭킹**: 검색결과 재정렬.
- **MCP**: 에이전트↔도구 표준 프로토콜(JSON-RPC). **A2A**: 에이전트끼리 통신.
- **관측**: LangSmith/Langfuse. **평가**: RAGAS/LLM-judge. **배포**: FastAPI+Docker.

---

## 학습 지도

```
[자작 코어 — 원리]                    [프레임워크 — 취업]
Phase 0  생 LLM 호출
Phase 1  tool use 직접 짜기    ──────►  L1  LangGraph 재구현 ★
Phase 2~5 언리얼 브릿지+통합            L3  RAG + 벡터DB
Phase 6  엔진 판정                     L4  멀티에이전트
Phase 7  비전                          L5  평가+관측
Phase 8  지식베이스           ──────►  L6  배포(FastAPI+Docker)
Phase 9  결정성+리포트                 L7  인젝션 방어
Phase 10 MCP 자작            ──────►  L2  MCP 표준화 ★
```

## 취업 우선순위 (시장 기준)

1. LangGraph (L1) — 최고연봉, 프로덕션 지배
2. MCP 저작 (L2) — 수요 급상승, 자작 중이라 유리
3. RAG + 벡터DB (L3) — 거의 모든 공고
4. 평가/관측 (L5) — 시니어 구분점
5. CrewAI/AutoGen (L4) — 스택 따라

---

## 리스크 / 미리 알 것

- **실시간성**: LLM 느림(초 단위). 실시간 반응 게임엔 부적합 → `slomo`/pause로 시간 정지/가속 테스트.
- **스크린샷 비용**: 매 틱 비전 = 느리고 비쌈 → 온디맨드만.
- **결정성**: 같은 테스트 = 같은 결과. 랜덤 시드 고정(`ResetScenario(seed)`).
- **스코프 폭발**: 범용 Codex 클론 금지. 게임 테스트에만 고정. (코드 자동수정은 한참 뒤 선택지)
- **구독 계정 호출**: 비공식/불안정 → console API 키 사용.

## 다음 할 일

- **Phase 0 시작**: 생 HTTP로 Claude API 호출 (curl → Python `requests`).

## 참고 프로젝트 (베끼지 말고 읽기)


| 프로젝트                 | 훔칠 것                          |
| -------------------- | ----------------------------- |
| ChiR24/Unreal_mcp    | 커스텀 MCP 도구 C++ 등록 패턴          |
| GamingAgent / Cradle | 에이전트 루프: 관찰→목표→행동→반성          |
| GameGuard            | assertion 변환, 회귀 diff, 버그 리포트 |
| Gauntlet (공식)        | 나중에 CI 감싸기                    |


## 출처

- Unreal MCP (UE 5.8 공식): dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor
- AI Agent 시장/프레임워크: turing.com/resources/ai-agent-frameworks, langchain.com/state-of-agent-engineering

