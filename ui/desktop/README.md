# Desktop (Electron)

에이전트를 감싸는 데스크탑 앱. **파이썬 뇌는 그대로**, 여긴 화면만.

## 구조
- `main/`      — Electron 메인 프로세스(Node, OS 권한). 창 생성 + 파이썬 spawn.
- `renderer/`  — 화면(웹기술 HTML/CSS/JS). 이벤트 표시 + 입력.
- `package.json` — Node 의존성 / 실행 스크립트 / 앱 메타.

## 통신 흐름
```
renderer(화면) ─IPC→ main(Node) ─spawn/stdio→ python -m ui.backend.run → agent/loop
     ↑──────────────────── 이벤트(JSON) ────────────────────────────────┘
```
파이썬이 stdout 으로 JSON 이벤트를 흘리고, Electron main 이 읽어 renderer 로 전달.
왜 이 방식: Electron=JS, 에이전트=Python 이라 직접 import 불가 → 프로세스 분리 + JSON 통신.

## 실행 (나중)
```
cd ui/desktop
npm install --save-dev electron
npm start
```

## 지금 상태
뼈대 + 각 파일 주석만. 채우는 시점 = 데스크탑 UI 붙일 때(D9).
그 전까지는 개발 테스트를 `python -m ui.backend.run` 으로 대신한다.
