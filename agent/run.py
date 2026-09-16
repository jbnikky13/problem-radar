from __future__ import annotations

from .analyzer import cluster, extract
from .report import generate
from .sources import collect
from .storage import ensure_started, load_observations, merge_observations, research_active, save_clusters


def main() -> None:
    state = ensure_started()
    active = research_active()
    if not active:
        state["status"] = "complete"
        print("[radar] Seven-day research window is complete. No new collection performed.")
        existing = [
            __import__("agent.models", fromlist=["Cluster"]).Cluster(**item)
            for item in __import__("json").loads(open("data/clusters.json", encoding="utf-8").read())
        ] if __import__("pathlib").Path("data/clusters.json").exists() else []
        generate(existing, len(load_observations()), False)
        return

    print(f"[radar] Research started: {state['started_at']}")
    raw = collect()
    observations = extract(raw)
    all_observations = merge_observations(observations)
    parsed = [__import__("agent.models", fromlist=["Observation"]).Observation(**item) for item in all_observations]
    clusters = cluster(parsed)
    save_clusters(clusters)
    generate(clusters, len(all_observations), True)
    print(f"[radar] collected={len(raw)} candidates={len(observations)} total={len(all_observations)} clusters={len(clusters)}")


if __name__ == "__main__":
    main()
