---
memoc: true
type: wiki
scope: project-memory
version: 0.3.0
created: 2026-07-23
updated: 2026-07-27
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

> Version 0.3.0 · 2026-07-27

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
| D4  | LLM = 멀티프로바이더 (Claude/OpenAI/DeepSeek), API 키 + dotenv | 구독 호출은 비공식/불안정 → API 키. OpenAI·DeepSeek은 API 모양 동일, Claude만 독자 |
| D5  | 라이브러리 0개 자작                               | 생 HTTP + 생 소켓 + JSON. SDK/공식MCP/LangChain X |
| D6  | 통제 패턴 = Tool Use 직접 구현                    | tool_use/tool_result 루프 = 에이전트 심장           |
| D7  | 브릿지 프로토콜: 자체 JSON → 나중에 진짜 MCP            | A→B 학습 사다리                                  |
| D8  | 고수준 액션 우선 + 엔진 assertion                  | LLM에 성공판정 시키지 마. 엔진이 `boss.hp==0` 판정        |
| D9  | UI = Electron 데스크탑. Python 뇌와 프로세스 분리, stdio JSON 통신 | 직접 import 불가(JS↔Py) → ui/backend/run.py를 spawn. 뼈대는 지금, 구현은 나중 |
| D10 | 언리얼 최신(5.8) 대상                            | 공식 MCP 존재하나 재사용 안 함(자작 학습 목적)               |
| D11 | 미래 구조 선반영 (빈 폴더 미리 생성)                    | 나중에 "이 파일 어디 두지" 고민 제거. 도구 추가 시 폴더만 채움      |
| D12 | 실행은 레포 루트에서 `python -m ui.backend.run`   | 폴더 분리 시 import 깨짐 방지. 모든 패키지에 `__init__.py`, import는 루트 절대경로 |
| D13 | 출력은 이벤트 콜백(`on_event`)으로 루프 밖에 위임         | 루프 안 `print` 금지. CLI→Streamlit→FastAPI 갈아끼워도 루프 무수정 |
| D14 | 언리얼 프로젝트 폴더명 = `ai_agent_test/` (레포 루트 바로 밑) | 플러그인은 그 바로 아래. `unreal/` 대신 실제 프로젝트명 사용      |


---

## 아키텍처

```
┌─ 에이전트 (Python, 100% 자작) ──────────────────────┐
│  llm_client.py   ← 생 HTTP, Claude API 직접 호출     │
│  tools.py        ← 도구 JSON schema 정의             │
│  agent_loop.py   ← tool_use/tool_result 루프 직접    │
│  bridge_client.py← 언리얼로 명령 (자체 프로토콜)      │
│  knowledge/, scenarios/, reports/                    │
│  (UI: Electron 데스크탑 ← stdio JSON, D9)             │
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

### 폴더 구조 (최상위 4분할)

미래 구조를 지금 미리 세움(D11). `★` = Phase 1에서 실제 생성.

```
ai_unreal_tester/
├── .venv/                          # Python 3.12.13 (gitignore)
├── .env / .env.example             # API 키 — 레포 루트 공용 (.env는 gitignore)
│
├── agent/                          # 파이썬 뇌
│   ├── __init__.py             ★
│   ├── requirements.txt            # requests + python-dotenv 만
│   │
│   ├── llm/                        # [입] 프로바이더 — 누구에게 묻나
│   │   ├── __init__.py         ★
│   │   ├── base.py             ★   LLMProvider 추상 규약
│   │   ├── claude.py           ★   Anthropic 생 HTTP (Phase 1 유일 구현)
│   │   ├── openai.py               (나중)
│   │   └── deepseek.py             (나중)
│   │
│   ├── tools/                      # [손] 도구 — 뭘 할 수 있나
│   │   ├── __init__.py         ★   레지스트리(스펙 수집 + 이름→실행)
│   │   ├── base.py             ★   Tool 규약(name/description/schema/run)
│   │   ├── builtin/                게임 무관 기본 도구
│   │   │   ├── __init__.py     ★
│   │   │   ├── time_tool.py    ★   get_time (인자 없는 도구)
│   │   │   └── math_tool.py    ★   add_numbers (인자 있는 도구 = 게임 도구와 같은 모양)
│   │   └── game/                   게임 도구 (Phase 3+)
│   │       ├── __init__.py     ★   (빈 껍데기)
│   │       ├── state.py            get_game_state
│   │       ├── action.py           perform_action / press_input
│   │       ├── vision.py           capture_view
│   │       └── assertion.py        evaluate_assertions
│   │
│   ├── loop/                       # [뇌] 판단 루프
│   │   ├── __init__.py         ★
│   │   ├── agent_loop.py       ★   tool_use/tool_result 왕복 (Phase 1 핵심)
│   │   ├── events.py           ★   진행 이벤트 타입 (출력 분리, D13)
│   │   └── session.py              대화기록/토큰 누적 (Phase 1 후반)
│   │
│   ├── bridge/                     # 언리얼 통신 (Phase 2+)
│   │   ├── __init__.py         ★
│   │   └── client.py               자체 JSON 프로토콜 클라이언트
│   │
│   ├── knowledge/  .gitkeep    ★   keymap.yaml, goals.yaml (Phase 8)
│   ├── scenarios/  .gitkeep    ★   테스트 시나리오 (Phase 8)
│   └── reports/                    결과물 (Phase 9, gitignore)
│
├── ui/                             # [화면] 진입점
│   ├── __init__.py             ★
│   ├── backend/                    파이썬↔데스크탑 다리 (Electron이 spawn)
│   │   ├── __init__.py         ★
│   │   └── run.py              ★   loop 실행 → on_event를 stdout JSON으로. 개발 진입점도 겸함
│   └── desktop/                    Electron 앱 (JS, 화면) — D9
│       ├── package.json        ★   Node 의존성/스크립트/앱 메타
│       ├── main/                   메인 프로세스(Node, OS 권한)
│       │   ├── main.js         ★   앱 진입점: 창 생성/수명주기
│       │   ├── preload.js      ★   contextBridge 안전 다리
│       │   └── agent-process.js ★  python -m ui.backend.run spawn + JSON 수신
│       ├── renderer/               화면(웹기술)
│       │   ├── index.html      ★   UI 뼈대
│       │   ├── renderer.js     ★   이벤트 표시 + 입력
│       │   └── styles.css      ★
│       └── README.md           ★   구조/실행법
│
├── mcp/                            # MCP 자작 (Phase 10)
│   └── README.md               ★
│
└── ai_agent_test/                  # 언리얼 5.8 프로젝트 (D14)
    └── (플러그인 AITesterBridge를 이 바로 밑에)
```

- 폴더명 소문자, 하이픈 X (파이썬 import). dotenv로 `.env` 키 로드.
- 빈 폴더는 git이 추적 안 함 → `.gitkeep` 또는 `README.md` 하나 넣어야 커밋됨.

#### 자리만 잡아두는 곳 (내용은 해당 Phase에서 채움)

| 경로 | 지금 상태 | 채우는 시점 |
| --- | --- | --- |
| `mcp/README.md` | 한 줄 메모: `Phase 10: 자체 프로토콜 → MCP 재구현` | Phase 10 |
| `ui/desktop/*` | 뼈대+주석만 (JS 빈 구현) | **#2 Electron MVP** |
| `ui/backend/run.py` | 동작 중 (`cli_print`로 터미널 출력) | #2 1~2단계에서 JSON stdout + stdin 루프 추가 |
| `agent/tools/game/` | `__init__.py`만 (빈 껍데기) | Phase 3~7, 도구별 파일 추가 |
| `agent/bridge/client.py` | 없음 | Phase 2 (언리얼 소켓 붙일 때) |
| `agent/loop/session.py` | 없음 | Phase 1 후반 (토큰 누적/대화기록) |
| `agent/knowledge/`, `agent/scenarios/` | `.gitkeep`만 | Phase 8 (YAML) |
| `ai_agent_test/` (언리얼) | **생성 안 함** | Phase 2 — 언리얼 에디터가 프로젝트 생성 시 직접 만듦 |

### 의존 방향 (한 방향만)

```
ui/backend/run.py  (← Electron desktop이 spawn)
      ↓
agent/loop/agent_loop.py
      ↓                ↓
agent/llm/*      agent/tools/*
```

- `llm/`이 `tools/`를 import ❌ (통신 담당은 도구를 몰라야 함)
- `tools/`가 `loop/`를 import ❌ (순환)
- 화살표가 거꾸로 가면 설계가 틀린 것.

### 파일별 경계 — "모르는 것"이 더 중요

| 파일 | 아는 것 | 모르는 것 ❌ |
| --- | --- | --- |
| `ui/backend/run.py` | loop 호출, 이벤트→JSON stdout | 화면 렌더링, HTTP |
| `ui/desktop/main/*.js` | 창 생성, 파이썬 spawn, IPC | 에이전트 내부 로직 |
| `loop/agent_loop.py` | messages, stop_reason, 턴 수 | HTTP·API키, print, datetime |
| `loop/events.py` | 진행 데이터 모양 | 누가 출력하는지 |
| `llm/base.py` | `call(messages, tools)` 규약 | Anthropic이 뭔지 |
| `llm/claude.py` | URL, 헤더, requests, 에러 | 도구가 뭔지, 루프가 있는지 |
| `tools/base.py` | 도구 공통 모양 | 특정 도구 내용 |
| `tools/__init__.py` | 스펙 수집, 이름→실행, 예외 흡수 | Claude, HTTP |
| `tools/builtin/time_tool.py` | datetime | Claude, 루프 |

### 실행 방법 (D12)

```bash
cd ai_unreal_tester
python -m ui.backend.run "지금 몇시야?"   # ✅ (개발 진입점; Electron도 이 모듈 spawn)
python ui/backend/run.py "..."          # ❌ ModuleNotFoundError
```

import은 항상 루트부터 절대경로: `from agent.llm.claude import ClaudeProvider`.
상대 import(`from ..llm import`) 쓰지 말 것.

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


### Phase 1 작업 순서 (아래 → 위, 단계마다 검증)

| # | 만들 것 | 검증 방법 |
| - | --- | --- |
| 1 | 폴더 전체 + `__init__.py` | `python -c "import agent.llm, agent.tools, agent.loop"` 무에러 |
| 2 | `llm/base.py` → `llm/claude.py` | 콘솔에서 `call([...])` → 응답 dict 확인. 이후 `loop.py` 삭제 |
| 3 | `tools/base.py` → `builtin/time_tool.py` → `tools/__init__.py` | `registry.execute("get_time", {})` 시각 반환 |
| 4 | `loop/events.py` | dataclass 5종 (TurnStart/ToolCall/ToolResult/FinalText/Usage) |
| 5 | `loop/agent_loop.py` | 핵심. 아래 함정 표 참고 |
| 6 | `ui/backend/run.py` | `python -m ui.backend.run "지금 몇시야?"` (on_event→출력) |

**완료 기준**
- `"지금 몇시야?"` → 턴1 도구 호출, 턴2 최종답
- `"안녕"` → 턴1 바로 `end_turn` (도구 안 씀 = 정상 동작)

### Phase 1 함정 (전원 여기서 막힘)

| 증상 | 원인 |
| --- | --- |
| `400 invalid tool_use_id` | 응답의 `id`를 그대로 안 씀 |
| 400 / 도구 무한 반복 | assistant 턴 append 누락 (`{"role":"assistant","content": data["content"]}` 배열 통째로) |
| 400 unresolved tool_use | 한 턴에 도구 2개인데 1개만 응답. **전부** 줘야 함 |
| 400 content 타입 | tool_result 담는 user 메시지 `content`는 **반드시 배열** |
| `TypeError: string indices` | `data["content"]`는 항상 블록 배열. `text`+`tool_use`가 같이 옴 |
| 크레딧 순삭 | `max_turns` 안 걸음 (기본 10) |

---

## #2 — Electron MVP (Phase 1 완료 후, Phase 2 이전)

**목표**: 터미널 대신 창에서 질문하고, 도구 사용 과정을 실시간으로 본다.

### 왜 프로세스를 나누나

Electron = JavaScript, 에이전트 = Python → 직접 import 불가. 텍스트 줄로만 대화한다.

```
Electron (JS)  ──spawn──▶  python -m ui.backend.run
     ▲                            │
     └──── stdout: JSON 한 줄 ────┘
        stdin: 질문 한 줄 ───────▶
```

### 통신 규약

**Python → Electron** (stdout, 한 줄 = JSON 1개). `agent/loop/events.py` dataclass를 그대로 직렬화:

```json
{"type":"TurnStart","turn":1,"stop_reason":"tool_use"}
{"type":"ToolCall","name":"get_time","input":{}}
{"type":"ToolResult","name":"get_time","output":"...","is_error":false}
{"type":"FinalText","text":"지금 오후 1시 20분입니다."}
{"type":"Usage","input_tokens":1474,"output_tokens":110}
```

- 한 줄에 JSON 하나(`\n` 구분) · `type` = 파이썬 클래스명(JS가 분기) · **stdout엔 JSON만**(디버그는 stderr)

**Electron → Python** (stdin, 한 줄 = 요청 1개):

```json
{"type":"ask","question":"지금 몇시야?","provider":"claude"}
```

→ `run.py`가 argv 1회성에서 stdin 대기 루프로 바뀜(창을 닫지 않고 계속 질문).

### 작업 순서

| # | 무엇 | 검증 |
| - | --- | --- |
| 1 | `run.py`: `json_print` 추가 (`cli_print` 유지) | `--json` 실행 → JSON 줄만 출력 |
| 2 | `run.py`: stdin 루프 | 터미널에 JSON 붙여넣기 → 응답 |
| 3 | `main.js` + `index.html`: 창 띄우기 | `npm start` → 빈 창 |
| 4 | `agent-process.js`: spawn + 줄 파싱 → IPC | 창에 이벤트 흐름 |
| 5 | `renderer.js`: 입력창 + 로그 + 프로바이더 드롭다운 | 창에서 질문 → 실시간 표시 |

1·2번은 Electron 없이 터미널만으로 검증된다. 거기까지면 나머지는 JS 배관.

### 함정

| 함정 | 대응 |
| --- | --- |
| stdout 오염 | 디버그 출력은 전부 `file=sys.stderr` |
| 줄 쪼개짐 | stdout이 청크로 도착 → JS에서 버퍼 쌓고 `\n` 기준으로만 파싱 |
| 버퍼링 지연 | `print(..., flush=True)` 또는 `python -u` |
| 경로/venv | spawn 시 `.venv/bin/python` 절대경로 + cwd=레포 루트 명시 |

### 디자인 방침 (조사 결과 2026-07-27)

| 도구 | 성격 | 결론 |
| --- | --- | --- |
| **UI UX Pro Max** (Claude Code 스킬) | 디자인 DB — 스타일 84·팔레트 192·폰트 74·UX 가이드 98, HTML/CSS 스택 지원 | **채택**. 설치형 스킬이라 프로젝트 의존성 0. 디자인 근거로만 사용 |
| **framer-motion** 12.42.2 (MIT) | `peerDependencies: react ^18\|\|^19` — **React 전용** | **보류**. vanilla 렌더러에 React를 끌어오는 건 MVP 과잉 |
| **motion** 12.42.2 (MIT) | 같은 팀의 vanilla `animate()` DOM API, `motion/mini` ≈2.6KB | 예비. CSS로 부족할 때만 ESM 파일 1개 복사 |

- **MVP는 CSS만**(`transition`, `@keyframes`). Electron 렌더러는 번들러 없이 npm 패키지를 import 못 하므로 CSS로 가면 그 문제 자체가 없다.
- 나중에 React+Vite로 갈아탈 때 framer-motion 재검토.
- UI UX Pro Max 설치: `/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill` → `/plugin install ui-ux-pro-max@ui-ux-pro-max-skill`

### 스코프 (MVP 고정)

- **넣음**: 질문 입력, 이벤트 로그, 토큰 표시, 프로바이더 드롭다운
- **뺌**: 대화 히스토리 저장, 설정 화면, 패키징(.app), 자동 업데이트, 정교한 디자인
- 폼은 진짜 게임 데이터가 나온 뒤에 잡는다. 지금은 흐름만 보이면 된다.

### 사전 준비

Node.js (`node -v`, 없으면 `brew install node`) → `ui/desktop/`에서 `npm install electron --save-dev`

---

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

## 진행 상황

- ✅ **Phase 0 완료** (2026-07-24): 생 HTTP로 Claude 호출. requests+dotenv, 응답/토큰/stop_reason 파싱. (`hello.py`는 구조 분리 후 제거)
- ✅ **Phase 1 완료** (2026-07-25): Tool Use 루프 자작. `get_time`/`add_numbers`로 단일·병렬 도구 호출 확인. 구조 분리 완료(`agent/llm·tools·loop·bridge`, `ui/backend·desktop`).
- ✅ **#1 멀티프로바이더 완료** (2026-07-25): `agent/llm`에 Claude/OpenAI/DeepSeek + `LLMResponse` 정규화. 루프는 프로바이더 무관.
- ✅ **환경 정리** (2026-07-27): Python 3.12.13 단일 venv, `.env`를 레포 루트로 통일, 3.9 잔재 venv 제거.
- ▶ **#2 Electron MVP 진행 예정**: 위 "#2 — Electron MVP" 섹션 참조. 1단계(`run.py` JSON 출력)부터.
- ⏳ **#3 Phase 2 언리얼**: `ai_agent_test/` 생성 + AITesterBridge 플러그인 + ping/pong.

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

