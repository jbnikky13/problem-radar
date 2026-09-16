from __future__ import annotations

import json
from pathlib import Path

from .analyzer import cluster, extract
from .heartbeat import record, record_complete
from .report import generate
from .sources import collect
from .storage import ensure_started, load_observations, merge_observations, research_active, save_clusters


def main() -> None:
    state = ensure_started()
    if not research_active():
        state["status"] = "complete"
        existing = [
            __import__("agent.models", fromlist=["Cluster"]).Cluster(**item)
            for item in json.loads(Path("data/clusters.json").read_text(encoding="utf-8"))
        ] if Path("data/clusters.json").exists() else []
        total = len(load_observations())
        record_complete(total, len(existing))
        generate(existing, total, False)
        print("[radar] Seven-day research window is complete. No new collection performed.")
        return

    print(f"[radar] Research started: {state['started_at']}")
    raw = collect()
    observations = extract(raw)
    all_observations = merge_observations(observations)
    parsed = [__import__("agent.models", fromlist=["Observation"]).Observation(**item) for item in all_observations]
    clusters = cluster(parsed)
    save_clusters(clusters)
    generate(clusters, len(all_observations), True)
    record(
        status="success",
        raw=len(raw),
        candidates=len(observations),
        total=len(all_observations),
        clusters=len(clusters),
    )
    print(f"[radar] collected={len(raw)} candidates={len(observations)} total={len(all_observations)} clusters={len(clusters)}")


if __name__ == "__main__":
    main()
