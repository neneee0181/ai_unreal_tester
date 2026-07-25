// preload.js — 렌더러 ↔ 메인 안전 다리 (contextBridge).
// 역할: renderer(화면)에 딱 필요한 API만 노출 (질문 보내기 / 이벤트 구독 등).
// 보안: renderer 가 Node 전체를 못 만지게 막고, 정해진 통로만 연다.
// 채우는 시점: 데스크탑 붙일 때.
