// agent-process.js — 파이썬 에이전트 프로세스 관리.
//
// 역할:
//   · `python -m ui.backend.run --json` 을 자식 프로세스로 spawn (레포 루트에서)
//   · 파이썬 stdout 의 JSON 이벤트를 "줄 단위"로 읽어 onEvent 로 넘김
//   · ask() 로 질문을 파이썬 stdin 에 써 넣음
// 안다: 프로세스 spawn / stdio / JSON 파싱.  모른다: 화면, 에이전트 내부 로직.

const { spawn } = require("child_process");
const path = require("path");
const readline = require("readline");

// 이 파일 위치: ui/desktop/main/agent-process.js
//   → 레포 루트는 세 단계 위 (main → desktop → ui → 루트)
const REPO_ROOT = path.join(__dirname, "..", "..", "..");

// 파이썬 실행 파일: 프로젝트 가상환경(agent/.venv) 우선, 없으면 시스템 python.
//   Windows 는 Scripts/python.exe, 그 외는 bin/python.
function pythonPath() {
  if (process.platform === "win32") {
    return path.join(REPO_ROOT, "agent", ".venv", "Scripts", "python.exe");
  }
  return path.join(REPO_ROOT, "agent", ".venv", "bin", "python");
}

function startAgent({ onEvent }) {
  // -u : 파이썬 출력 버퍼 끔 (이벤트를 실시간으로 받기 위해)
  const child = spawn(pythonPath(), ["-u", "-m", "ui.backend.run", "--json"], {
    cwd: REPO_ROOT,          // 여기서 실행해야 `-m ui.backend.run` 이 풀린다 (D12)
    // PYTHONUTF8=1 : Windows 에서도 파이썬 stdio 를 UTF-8 로 (한글 깨짐 방지)
    env: { ...process.env, PYTHONUTF8: "1" },
  });

  // stdout 을 "한 줄 = 이벤트 하나"(JSON Lines)로 읽는다.
  const rl = readline.createInterface({ input: child.stdout });
  rl.on("line", (line) => {
    line = line.trim();
    if (!line) return;
    try {
      onEvent(JSON.parse(line));          // JSON 한 줄 → 화면으로
    } catch {
      // JSON 아닌 줄(디버그 print 등)은 그냥 콘솔에만
      console.log("[py]", line);
    }
  });

  // 파이썬 에러(stderr)는 개발용 콘솔에 그대로
  child.stderr.on("data", (d) => console.error("[py-err]", d.toString()));
  child.on("exit", (code) => console.log("[py] 종료 code=", code));

  return {
    // 질문 보내기: stdin 에 JSON 한 줄 써 넣기 (파이썬이 줄 단위로 읽음)
    ask: (request) => child.stdin.write(JSON.stringify(request) + "\n"),
    // 앱 종료 시 파이썬도 정리
    stop: () => child.kill(),
  };
}

module.exports = { startAgent };
