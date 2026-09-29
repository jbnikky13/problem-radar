from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


def run_audit() -> dict:
    path = DATA / "observations.json"
    try:
        observations = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        observations = []
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_observations": len(observations),
        "categories": dict(Counter(x.get("category", "other") for x in observations)),
        "source_domains": dict(Counter(x.get("source_domain", "unknown") for x in observations)),
    }
    (DATA / "audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "evidence-audit.md").write_text(
        "# Problem Radar Evidence Audit v2\n\n"
        f"Generated: {result['generated_at']}\n\n"
        f"Raw observations: {result['raw_observations']}\n\n"
        "This audit pass records the raw dataset baseline. A subsequent pass will add source resolution, duplicate/event grouping, and evidence filtering.\n",
        encoding="utf-8",
    )
    return result
