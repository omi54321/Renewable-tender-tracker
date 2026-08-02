from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_hash(record: dict[str, Any]) -> str:
    payload = json.dumps(record, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
