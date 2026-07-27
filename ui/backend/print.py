import json

from dataclasses import asdict

def json_print(event) -> None:
    """이벤트를 Electron이 읽을 JSON 한 줄로 출력한다."""

    payload = {
        "type": type(event).__name__,
        **asdict(event),
    }

    print(
        json.dumps(payload, ensure_ascii=False),
        flush=True,
    )