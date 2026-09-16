from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import CONFIG
from .models import Cluster, Observation

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OBSERVATIONS = DATA / "observations.json"
CLUSTERS = DATA / "clusters.json"
STATE = DATA / "state.json"


def _read(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write(path: Path, value):
    DATA.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def load_state() -> dict:
    return _read(STATE, {})


def save_state(state: dict):
    _write(STATE, state)


def research_active() -> bool:
    state = load_state()
    if not state.get("started_at"):
        return True
    started = datetime.fromisoformat(state["started_at"])
    elapsed = datetime.now(timezone.utc) - started
    return elapsed.total_seconds() < CONFIG.research_days * 86400


def ensure_started() -> dict:
    state = load_state()
    if not state.get("started_at"):
        state = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "research_days": CONFIG.research_days,
            "status": "active",
        }
        save_state(state)
    return state


def load_observations() -> list[dict]:
    return _read(OBSERVATIONS, [])


def merge_observations(observations: list[Observation]) -> list[dict]:
    existing = {item["id"]: item for item in load_observations()}
    for observation in observations:
        existing[observation.id] = observation.to_dict()
    result = sorted(existing.values(), key=lambda x: x.get("collected_at", ""), reverse=True)
    _write(OBSERVATIONS, result)
    return result


def save_clusters(clusters: list[Cluster]):
    _write(CLUSTERS, [cluster.to_dict() for cluster in clusters])
