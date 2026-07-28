// App.jsx — 화면 전체 (React 컴포넌트 하나).
//
// 큰 그림:
//   [드롭다운으로 프로바이더 선택] + [질문 입력] → window.agent.ask() 로 파이썬에 전송
//   파이썬이 뱉는 이벤트 → window.agent.onEvent() 로 받아 목록에 쌓고 화면에 그림
//   애니메이션 → framer-motion 의 <motion.*> 로 부드럽게 등장
//
// React 기본 개념 2개만 알면 됨:
//   · useState : "변하는 값"을 담는 상자. 값이 바뀌면 화면이 자동으로 다시 그려진다.
//   · useEffect: "화면 뜰 때 한 번" 같은 부수효과 실행 (여기선 이벤트 구독).

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

// 이벤트 종류(type) → 화면에 보일 라벨/색. 파이썬 events.py + run.py 와 짝.
const EVENT_META = {
  TurnStart:    { label: "턴 시작",   color: "#8b5cf6" },
  AssistantText:{ label: "LLM 중간말", color: "#6366f1" },
  ToolCall:     { label: "도구 호출", color: "#0ea5e9" },
  ToolResult:   { label: "도구 결과", color: "#10b981" },
  FinalText:    { label: "최종 답",   color: "#22c55e" },
  LimitReached: { label: "턴 한도",   color: "#f59e0b" },
  Usage:        { label: "토큰 사용", color: "#64748b" },
  Error:        { label: "오류",      color: "#ef4444" },
};

// 이벤트 하나를 사람이 읽을 문장으로 변환
function eventText(e) {
  switch (e.type) {
    case "TurnStart":     return `턴 ${e.turn} (stop_reason=${e.stop_reason})`;
    case "AssistantText": return e.text;
    case "ToolCall":      return `${e.name}(${JSON.stringify(e.input)})`;
    case "ToolResult":    return e.output;
    case "FinalText":     return e.text;
    case "LimitReached":  return `턴 한도 ${e.max_turns} 초과로 중단`;
    case "Usage":         return `입력 ${e.input_tokens} · 출력 ${e.output_tokens} 토큰`;
    case "Error":         return e.message;
    default:              return JSON.stringify(e);
  }
}

export default function App() {
  const [provider, setProvider] = useState("claude"); // 드롭다운 선택값
  const [question, setQuestion] = useState("");        // 입력창 글자
  const [events, setEvents] = useState([]);            // 받은 이벤트 목록
  const [busy, setBusy] = useState(false);             // 답 기다리는 중?
  const logRef = useRef(null);                         // 로그 영역(자동 스크롤용)

  // ── 화면 뜰 때 한 번: 파이썬 이벤트 구독 ──
  useEffect(() => {
    // window.agent 는 preload 가 "Electron 안에서만" 심어준다.
    // 일반 브라우저(localhost:5173 직접 열기)엔 없음 → 크래시 대신 조용히 건너뜀.
    if (!window.agent) {
      console.warn("window.agent 없음 — Electron 창이 아니라 브라우저임. 앱 창을 보세요.");
      return;
    }
    // onEvent 는 preload 가 심어준 통로. 이벤트가 올 때마다 콜백 실행.
    const unsubscribe = window.agent.onEvent((e) => {
      if (e.type === "Ready") return;          // 준비완료 신호는 무시
      if (e.type === "Done") { setBusy(false); return; } // 이번 답 끝 → 입력 다시 열기
      // 목록에 추가. id 는 애니메이션 key 용(순번).
      setEvents((prev) => [...prev, { ...e, id: prev.length }]);
    });
    return unsubscribe;   // 화면 사라질 때 구독 해제 (메모리 누수 방지)
  }, []);

  // 이벤트가 늘 때마다 로그 맨 아래로 스크롤
  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [events]);

  // 질문 보내기
  function send() {
    const q = question.trim();
    if (!q || busy) return;             // 빈 질문/응답중이면 무시
    if (!window.agent) {                 // 브라우저면 파이썬 연결 없음 → 안내만
      alert("Electron 앱 창에서 실행하세요 (브라우저는 파이썬과 연결 안 됨).");
      return;
    }
    setEvents([]);                       // 새 질문이면 이전 로그 비우기
    setBusy(true);
    window.agent.ask({ question: q, provider });  // → 메인 → 파이썬 stdin
    setQuestion("");
  }

  return (
    <div className="app">
      {/* 헤더: 제목 + 프로바이더 드롭다운 */}
      <header className="header">
        <h1>🎮 AI Unreal Tester</h1>
        <select
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          disabled={busy}
        >
          <option value="claude">Claude</option>
          <option value="openai">OpenAI</option>
          <option value="deepseek">DeepSeek</option>
        </select>
      </header>

      {/* 이벤트 로그 */}
      <div className="log" ref={logRef}>
        {/* AnimatePresence : 항목이 추가/제거될 때 애니메이션을 관리 */}
        <AnimatePresence initial={false}>
          {events.map((e) => {
            const meta = EVENT_META[e.type] || { label: e.type, color: "#94a3b8" };
            return (
              // motion.div = 애니메이션 가능한 div.
              //   initial : 처음 상태(투명 + 살짝 아래/왼쪽)
              //   animate : 목표 상태(불투명 + 제자리)
              //   transition : 얼마나/어떻게 (0.25초 부드럽게)
              <motion.div
                key={e.id}
                layout
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.25 }}
                className="event"
              >
                <span className="badge" style={{ background: meta.color }}>
                  {meta.label}
                </span>
                <span className="event-text">{eventText(e)}</span>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {/* 응답 대기 중이면 점 세 개 애니메이션 */}
        {busy && (
          <motion.div
            className="thinking"
            animate={{ opacity: [0.3, 1, 0.3] }}      // 깜빡깜빡 반복
            transition={{ repeat: Infinity, duration: 1.2 }}
          >
            생각 중…
          </motion.div>
        )}
      </div>

      {/* 입력 줄 */}
      <div className="input-row">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}  // 엔터로도 전송
          placeholder="질문 입력 (예: 지금 몇시야?)"
          disabled={busy}
        />
        {/* whileTap : 누르는 순간 살짝 작아짐 (촉감 피드백) */}
        <motion.button whileTap={{ scale: 0.94 }} onClick={send} disabled={busy}>
          보내기
        </motion.button>
      </div>
    </div>
  );
}
