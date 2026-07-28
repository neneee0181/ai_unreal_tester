// main.js — Electron 메인 프로세스 진입점 (Node.js 환경, OS 권한 있음).
//
// Electron 앱은 프로세스가 둘로 나뉜다:
//   · 메인(main)     : 이 파일. 창 만들기, 파일/OS 접근, 파이썬 spawn.
//   · 렌더러(renderer): 화면(React). 브라우저처럼 샌드박스 안. OS 직접 못 만짐.
// 둘은 preload(안전 다리) + IPC(메시지)로만 대화한다. → 보안.
//
// 이 파일이 하는 일:
//   1) 창(BrowserWindow) 하나 만들고 화면(React) 로드
//   2) 파이썬 에이전트 프로세스 시작 (agent-process.js)
//   3) 화면 ↔ 파이썬 사이 메시지 중계 (IPC)

const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const { startAgent } = require("./agent-process");

let win = null;      // 창 참조 (가비지컬렉션 방지용으로 밖에 둔다)
let agent = null;    // 파이썬 프로세스 핸들

function createWindow() {
  win = new BrowserWindow({
    width: 900,
    height: 680,
    webPreferences: {
      // preload : 화면이 뜨기 직전 실행돼 window.agent API 를 심는다.
      preload: path.join(__dirname, "preload.js"),
      // 아래 둘이 보안 핵심. 화면이 Node 를 직접 못 쓰게 막는다.
      contextIsolation: true,   // 화면 JS 와 preload JS 세계 분리
      nodeIntegration: false,   // 화면에서 require() 금지
    },
  });

  // 화면 로드: 개발 중엔 Vite 개발서버(실시간 갱신), 배포 땐 빌드된 파일.
  //   VITE_DEV_SERVER_URL 은 package.json 의 dev 스크립트가 넣어준다.
  const devUrl = process.env.VITE_DEV_SERVER_URL;
  if (devUrl) {
    win.loadURL(devUrl);
    //win.webContents.openDevTools();          // 개발 땐 개발자도구 자동 오픈
  } else {
    win.loadFile(path.join(__dirname, "..", "renderer", "dist", "index.html"));
  }
}

// app 이 준비되면(=Electron 초기화 완료) 창을 만든다.
app.whenReady().then(() => {
  createWindow();

  // 파이썬 에이전트 시작. 두 콜백을 넘긴다:
  //   onEvent : 파이썬이 뱉은 이벤트 → 화면(renderer)으로 IPC 전송
  agent = startAgent({
    onEvent: (event) => {
      if (win) win.webContents.send("agent:event", event);
    },
  });

  // ── IPC: 화면 → 메인 방향 ──
  // 화면에서 window.agent.ask(...) 하면 여기로 온다. 파이썬 stdin 에 넘긴다.
  ipcMain.on("agent:ask", (_e, request) => {
    agent.ask(request);   // request = { question, provider }
  });

  // macOS: 독 아이콘 클릭 시 창 없으면 다시 생성
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// 창 다 닫히면 앱 종료 (macOS 관례는 예외지만 학습용이라 단순화)
app.on("window-all-closed", () => {
  if (agent) agent.stop();   // 파이썬 프로세스도 같이 정리
  app.quit();
});
