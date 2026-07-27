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
# Current Project State

Last synced: 2026-07-23T10:38:31

## Current Status

_See Project Snapshot below. Keep only current human-written status notes here._

## Project Snapshot

<!-- memoc:snapshot:start -->
- Last synced: 2026-07-27T04:19:12
- Detected stack: Not detected

### Config Files

- `.env.example`

### Source Directories

- `.agents`
- `.claude`
- `.venv`
- `.venv-1`
- `agent`
- `mcp`
- `ui`
<!-- memoc:snapshot:end -->

## Open Tasks

- **#2 Electron MVP** — `ui/backend/run.py` JSON 이벤트 stdout + stdin 질문 수신, `ui/desktop/*` spawn/IPC 구현, 프로바이더 드롭다운.
- **#3 Phase 2 언리얼** — `ai_agent_test/` 프로젝트 생성, AITesterBridge 플러그인, Python↔언리얼 ping/pong.

## Completed Tasks

See `.memoc/worklog/` for full shared activity history.

## Commands

레포 루트에서 실행 (D12). venv = `.venv/` (Python 3.12.13).

```bash
source .venv/bin/activate
python -m ui.backend.run "지금 몇시야?"        # 에이전트 루프 실행
LLM_PROVIDER=openai python -m ui.backend.run "..."   # 프로바이더 전환
python -m pip install -r agent/requirements.txt      # 의존성
sh .memoc/bin/memoc lint-wiki                        # 위키 검사
```

`.venv-1/`(Python 3.9 잔재) 삭제 완료(2026-07-27). gitignore는 `.venv*/`로 확장.

**`.env` 위치 = 레포 루트** (프로젝트 공용). `run.py`가 `parents[2]/.env`를 로드.
2026-07-27까지 실제 파일이 `agent/.env`에 남아 있어 경로 불일치였음 → 루트로 이동해 해결.
`load_dotenv`는 파일이 없어도 조용히 실패하므로 키 오류 시 위치부터 확인할 것.

## Notes

_None yet._

## Change Log

See `.memoc/worklog/` and generated `.memoc/activity.md`.
