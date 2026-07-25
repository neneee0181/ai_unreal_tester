"""Phase 1 학습용 — tool use 루프 최소 구현 (한 파일 버전).

이 파일은 원리를 눈으로 보기 위한 임시 파일이다.
동작을 이해한 뒤 agent/llm, agent/tools, agent/loop, ui/cli 로 쪼갠다.

실행:
    python agent/loop.py "지금 몇시야?"
    python agent/loop.py "안녕"          # 도구 안 씀 (정상)
"""

import os
import sys
from datetime import datetime
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5"
MAX_TURNS = 10   # 무한루프 방지 (크레딧 보호)


# ── [1] 도구 스펙 : Claude가 읽는 설명서 ──────────────────────────────
# description 이 Claude가 "언제 쓸지" 판단하는 유일한 근거다.

TOOLS = [
    {
        "name": "get_time",
        "description": "현재 시각을 ISO 형식 문자열로 반환한다. 사용자가 시간이나 날짜를 물으면 사용.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# ── [2] 실제 도구 함수 ────────────────────────────────────────────────

def get_time(**kwargs) -> str:
    return datetime.now().isoformat(timespec="seconds")


# 이름 → 함수. 도구가 늘어도 루프 코드는 안 고친다.
TOOL_FUNCS = {
    "get_time": get_time,
}


def execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """도구 실행. (결과문자열, 에러여부) 반환.

    예외를 여기서 흡수해야 도구가 터져도 루프가 안 죽는다.
    게임 테스트는 액션 실패가 일상이라 필수.
    """
    func = TOOL_FUNCS.get(name)

    if func is None:
        return f"에러: 알 수 없는 도구 '{name}'", True

    try:
        return str(func(**tool_input)), False
    except Exception as error:
        return f"에러: {error}", True


# ── [3] API 호출 : messages 를 인자로 받는다 (hello.py 와 다른 점) ──────

def call_claude(messages: list, api_key: str) -> dict:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    body = {
        "model": MODEL,
        "max_tokens": 500,
        "tools": TOOLS,        # ← 도구 목록을 매 호출마다 함께 보냄
        "messages": messages,
    }

    response = requests.post(API_URL, headers=headers, json=body, timeout=60)

    if response.status_code != 200:
        print(f"API 요청 실패 ({response.status_code})")
        print(response.text)
        sys.exit(1)

    return response.json()


# ── [4] 루프 : 에이전트의 심장 ────────────────────────────────────────

def run(question: str, api_key: str) -> None:
    # content 는 문자열(첫 질문)일 수도, 블록 배열(tool_result)일 수도 있다.
    # 그래서 값 타입을 Any 로 열어둔다.
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": question},
    ]

    total_in = 0
    total_out = 0

    for turn in range(1, MAX_TURNS + 1):

        # ① API 호출
        data = call_claude(messages, api_key)

        usage = data.get("usage", {})
        total_in += usage.get("input_tokens", 0)
        total_out += usage.get("output_tokens", 0)

        stop_reason = data.get("stop_reason")
        print(f"\n[턴 {turn}] stop_reason={stop_reason}")

        # ② 끝났으면 텍스트 출력하고 종료
        if stop_reason != "tool_use":
            for block in data.get("content", []):
                if block.get("type") == "text":
                    print(block.get("text", ""))
            break

        # 도구 부르기 전에 뭔가 말했으면 같이 보여준다
        for block in data.get("content", []):
            if block.get("type") == "text":
                print(f"  (Claude) {block.get('text', '')}")

        # ③ assistant 턴을 통째로 기록  ★ 이걸 빼면 400 에러
        messages.append({
            "role": "assistant",
            "content": data["content"],
        })

        # ④ tool_use 블록 전부 실행
        results: list[dict[str, Any]] = []   # is_error 는 bool 이라 Any 필요

        for block in data["content"]:
            if block.get("type") != "tool_use":
                continue

            name = block["name"]
            tool_input = block.get("input", {})
            print(f"  → 도구 호출: {name}({tool_input})")

            output, is_error = execute_tool(name, tool_input)
            print(f"  ← 결과: {output}")

            result_block = {
                "type": "tool_result",
                "tool_use_id": block["id"],   # ★ 받은 id 그대로
                "content": output,
            }

            if is_error:
                result_block["is_error"] = True

            results.append(result_block)

        # ⑤ 결과 전부를 한 개의 user 메시지로 되돌려준다
        messages.append({
            "role": "user",
            "content": results,
        })

    else:
        print(f"\n턴 한도({MAX_TURNS}) 초과. 중단.")

    print(f"\n=== 누적 토큰 : 입력 {total_in} / 출력 {total_out} ===")


def main() -> None:
    if len(sys.argv) < 2:
        print('사용법 : python agent/loop.py "claude에게 보낼 질문"')
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)

    run(" ".join(sys.argv[1:]), api_key)


if __name__ == "__main__":
    main()
