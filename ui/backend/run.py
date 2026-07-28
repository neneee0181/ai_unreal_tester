"""데스크탑 백엔드 진입점 — 개발 진입점 겸 Electron 이 spawn 할 대상.

역할(얇음): 프로바이더 고르고 → 루프(agent_loop.run) 돌리고 → 포맷터로 출력.
           "이벤트를 어떻게 보여주나"는 ui.backend.print 가 담당(D13).

두 가지 모드:
  1) CLI 모드   : `python -m ui.backend.run "질문"`      → 사람용 터미널 출력(cli_print)
  2) JSON 모드  : `python -m ui.backend.run --json`      → Electron 용 JSON 상주 서버
                   (질문을 stdin 으로 한 줄씩 계속 받는다)

핵심(D13): 루프(agent_loop.run)는 손 안 댄다. 바뀌는 건 on_event 콜백(포맷터)뿐.
"""

import os
import sys
import json
from pathlib import Path

# Windows 함정: 파이썬은 stdin/stdout 을 OS 로케일(한글 = cp949)로 읽고 쓴다.
# 하지만 Electron 은 UTF-8 로 주고받는다 → 한글/이모지가 깨져 lone surrogate 발생
#   → Claude 에 깨진 JSON 전송 → "invalid high surrogate" 400.
# 그래서 stdin/stdout 을 UTF-8 로 못박는다. (reconfigure = Python 3.7+)
for stream in (sys.stdin, sys.stdout):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

from agent.llm import get_provider
from agent.loop.agent_loop import run
from ui.backend.print import cli_print, json_print   # 출력 포맷터(분리됨)

# .env 는 레포 루트(프로젝트 공용 설정). 어디서 실행해도 찾도록 경로 명시.
#   ui/backend/run.py → parents[2] = 레포 루트
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def run_json_mode() -> None:
    """stdin 에서 질문을 한 줄씩 받아 루프를 돌리는 상주(persistent) 서버 모드.

    Electron 이 보내는 한 줄 = JSON:  {"question": "지금 몇시야?", "provider": "claude"}
    한 질문이 끝나면 {"type": "Done"} 을 찍어 "이번 답 끝" 을 알린다.
    프로세스는 살아있으면서 다음 질문을 기다린다.
    """
    print(json.dumps({"type": "Ready"}), flush=True)   # 준비완료 신호

    for line in sys.stdin:          # stdin 이 닫힐 때까지(=Electron 종료) 반복
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)                       # 한 줄 → dict
            question = req.get("question", "").strip()
            name = req.get("provider", "claude")         # 화면 드롭다운이 고른 값
            if not question:
                continue
            provider = get_provider(name)
            run(question, provider, on_event=json_print)  # 루프는 그대로, 콜백만 json
        except Exception as e:
            # 오류도 이벤트로 내보내 화면이 표시할 수 있게
            print(json.dumps({"type": "Error", "message": str(e)}), flush=True)
        print(json.dumps({"type": "Done"}), flush=True)   # 이번 질문 종료 신호


def main() -> None:
    # --json 이면 Electron 용 JSON 상주 서버
    if "--json" in sys.argv:
        run_json_mode()
        return

    # 그 외엔 CLI 모드: argv 로 질문 한 방 받고 끝
    if len(sys.argv) < 2:
        print('사용법 : python -m ui.backend.run "질문"   (또는 --json 으로 Electron 모드)')
        sys.exit(1)

    # 프로바이더 이름 — CLI 에선 환경변수로 전환: claude(기본) / openai / deepseek
    name = os.environ.get("LLM_PROVIDER", "claude")
    provider = get_provider(name)

    run(" ".join(sys.argv[1:]), provider, on_event=cli_print)


if __name__ == "__main__":
    main()
