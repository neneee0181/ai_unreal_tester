# mcp — MCP 자작 (Phase 10)

**Phase 10: 자체 JSON 프로토콜 → 진짜 MCP 재구현.**

지금은 자리만. 채우는 시점 = Phase 10.

## 배경 (plan D7)

- 학습 사다리 A→B:
  - **A (먼저)**: `agent/bridge` 의 자체 JSON 프로토콜로 언리얼과 통신 (Phase 2). 개념 먼저 체득.
  - **B (여기)**: 그 개념을 **표준 MCP 스펙**(JSON-RPC 2.0: `initialize`, `tools/list`, `tools/call`)으로 재구현.
- B가 되면 이 브릿지가 Claude Code / Cursor 같은 표준 MCP 클라이언트에도 붙는다.
- 스펙: modelcontextprotocol.io
