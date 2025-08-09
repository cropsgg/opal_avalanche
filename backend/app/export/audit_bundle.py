from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.core.config import get_settings


def write_audit_json(run_id: str, payload: Dict[str, Any]) -> str:
    base = Path(get_settings().EXPORT_TMP_DIR)
    base.mkdir(parents=True, exist_ok=True)
    p = base / f"audit-{run_id}.json"
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(p)


