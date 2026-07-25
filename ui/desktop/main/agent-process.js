// agent-process.js — 파이썬 에이전트 프로세스 관리.
// 역할: `python -m ui.backend.run` 을 spawn, stdout 의 JSON 이벤트 라인을 읽어
//        main → renderer(IPC) 로 전달. stdin 으로 사용자 질문 전달.
// 안다: 프로세스 spawn / stdio, JSON 파싱. 모른다: 화면, 에이전트 내부 로직.
// 채우는 시점: 데스크탑 붙일 때.
