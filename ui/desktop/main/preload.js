// preload.js — 렌더러(화면) ↔ 메인 사이의 "안전한 다리".
//
// 화면(React)은 보안상 Node/OS 를 직접 못 쓴다. 대신 preload 가
// window.agent 라는 "딱 필요한 API 몇 개"만 화면에 노출한다.
// → 화면은 이 좁은 통로로만 바깥과 대화한다. (해커가 화면을 뚫어도 피해 최소)

const { contextBridge, ipcRenderer } = require("electron");

// window.agent.xxx 형태로 화면에서 쓸 수 있게 심는다.
contextBridge.exposeInMainWorld("agent", {
  // 질문 보내기: 화면 → 메인 → 파이썬 stdin
  //   request = { question: "지금 몇시야?", provider: "claude" }
  ask: (request) => ipcRenderer.send("agent:ask", request),

  // 이벤트 구독: 파이썬 → 메인 → 화면
  //   callback 에 이벤트 하나(dict)가 들어온다. React 가 화면에 그린다.
  //   반환값은 "구독 해제 함수" (React useEffect 정리에 씀).
  onEvent: (callback) => {
    const handler = (_e, event) => callback(event);
    ipcRenderer.on("agent:event", handler);
    return () => ipcRenderer.removeListener("agent:event", handler);
  },
});
