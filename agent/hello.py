import os
import  sys

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5"

def main() -> None:

    if len(sys.argv) < 2:
        print('사용법 : python hello.py "claude에게 보낼 질문"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)


    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    body = {
        "model" : MODEL,
        "max_tokens" : 500,
        "messages" : [
            {
                "role": "user",
                "content": question
            }
        ]
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=body,
            timeout=60
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(f"API 요청 실패 : {error}")

        if "response" in locals():
            print(response.text)

        sys.exit(1)

    data = response.json()

    for block in data.get("content", []):
        if block.get("type") == "text":
            print(block.get("text", ""))

    usage = data.get("usage", {})

    print("\n=== 사용량 정보 ===")
    print(f"입력 토큰: {usage.get('input_tokens', 0)}")
    print(f"출력 토큰: {usage.get('output_tokens', 0)}")
    print(f"종료 이유 : {data.get('stop_reason')}")

    return;

if __name__ == "__main__":
    main()