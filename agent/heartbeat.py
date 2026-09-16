from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
HEARTBEAT = DATA / "heartbeat.json"


def record(*, status: str, raw: int, candidates: int, total: int, clusters: int) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": status,
        "last_successful_run": datetime.now(timezone.utc).isoformat(),
        "raw_items": raw,
        "new_problem_candidates": candidates,
        "total_observations": total,
        "clusters": clusters,
    }
    HEARTBEAT.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def record_complete(total: int, clusters: int) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "complete",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "total_observations": total,
        "clusters": clusters,
    }
    HEARTBEAT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
