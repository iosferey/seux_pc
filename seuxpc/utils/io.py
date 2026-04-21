import json
import os
from datetime import datetime
from urllib.parse import urlparse

def _safe_name(url: str) -> str:
    netloc = urlparse(url).netloc.replace("www.", "")
    return netloc.replace(":", "_")

def save_result_json(result: dict, url: str, out_dir: str = "outputs"):
    os.makedirs(out_dir, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name = _safe_name(url)
    path = os.path.join(out_dir, f"{name}_{ts}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return path