from __future__ import annotations

import json
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8090"
request_body = json.loads(
    (Path(__file__).parent / "http/retrieval_request.json").read_text(encoding="utf-8")
)
request = urllib.request.Request(
    f"{BASE_URL}/api/v1/retrieval/search",
    data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=30) as response:
    print(json.dumps(json.load(response), ensure_ascii=False, indent=2))
