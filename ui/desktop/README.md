# Desktop (Electron + React + Vite + framer-motion)

에이전트를 감싸는 데스크탑 앱. **파이썬 뇌는 그대로**, 여긴 화면만.

## 구조
- `main/`       — Electron 메인 프로세스(Node, OS 권한). 창 생성 + 파이썬 spawn + IPC 중계.
  - `main.js`          창 생성, 화면 로드, 이벤트 중계
  - `preload.js`       화면에 `window.agent` 안전 API 노출 (contextBridge)
  - `agent-process.js` `python -m ui.backend.run --json` spawn, stdout JSON 읽기
- `renderer/`   — 화면(React). Vite 가 빌드.
  - `index.html`       뼈대 (React 를 여기 심음)
  - `src/main.jsx`     React 시작점 (App 을 root 에 mount)
  - `src/App.jsx`      UI 전체 + framer-motion 애니메이션
  - `src/styles.css`   스타일 (다크 테마)
- `vite.config.js` — Vite 설정 (root=renderer, JSX 처리)
- `package.json`   — Node 의존성 / 실행 스크립트

## 통신 흐름
```
renderer(React) ─IPC→ main(Node) ─spawn/stdio→ python -m ui.backend.run --json → agent/loop
      ↑──────────────── 이벤트(JSON 한 줄씩) ─────────────────────────────────────┘
```
파이썬이 stdout 으로 이벤트를 JSON 한 줄씩 흘리고(run.py `json_print`), Electron main 이
줄 단위로 읽어 renderer 로 전달. 질문은 반대로 renderer → main → 파이썬 stdin.
왜 이 방식: Electron=JS, 에이전트=Python 이라 직접 import 불가 → 프로세스 분리 + JSON 통신(D9).

## 실행
```bash
cd ui/desktop
npm install          # 최초 1회 (react, framer-motion, electron, vite …)
npm run dev          # Vite 개발서버 + Electron 동시 실행 (화면 수정 즉시 반영)
```
- 백엔드만 터미널에서 테스트: 레포 루트에서 `python -m ui.backend.run "지금 몇시야?"`
- `agent/.venv` 가상환경 파이썬을 자동으로 씀 (agent-process.js).

## 배포 흉내
```bash
npm run build        # 화면을 renderer/dist 로 빌드
npm start            # 빌드본 로드해서 Electron 실행
```

## 애니메이션 (framer-motion) 배울 포인트 — `src/App.jsx`
- `<motion.div initial animate transition>` : 등장 애니메이션 (투명→불투명, 슬라이드)
- `<AnimatePresence>` : 목록 항목 추가/제거 시 부드럽게
- `whileTap={{scale:0.94}}` : 버튼 누를 때 촉감 피드백
- `animate={{opacity:[...]}} transition={{repeat:Infinity}}` : "생각 중…" 깜빡임
