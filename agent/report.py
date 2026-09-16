from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .models import Cluster

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def generate(clusters: list[Cluster], observation_count: int, active: bool) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    ranked = sorted(
        clusters,
        key=lambda c: (
            c.evidence_score + c.pain_score + c.recurrence_score + c.information_gap_score
            + c.automation_score + c.monetization_signal_score
        ),
        reverse=True,
    )
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        "# 🇳🇬 Nigeria Problem Radar — Latest Research",
        "",
        f"Generated: `{now}`",
        f"Research status: **{'ACTIVE' if active else 'COMPLETE'}**",
        f"Unique observations collected: **{observation_count}**",
        "",
        "> This is an evidence report, not an automatic business recommendation. Scores are research signals used to decide what to investigate next.",
        "",
        "## Top recurring problem clusters",
        "",
    ]
    for rank, cluster in enumerate(ranked[:20], start=1):
        lines += [
            f"### {rank}. {cluster.title}",
            f"**Category:** `{cluster.category}`  ",
            f"**Observations:** {cluster.observation_count}  ",
            f"**Evidence:** {cluster.evidence_score}/10  ",
            f"**Pain:** {cluster.pain_score}/10  ",
            f"**Recurrence:** {cluster.recurrence_score}/10  ",
            f"**Information gap:** {cluster.information_gap_score}/10  ",
            f"**Automation signal:** {cluster.automation_score}/10  ",
            f"**Monetization signal:** {cluster.monetization_signal_score}/10",
            "",
            "**Representative evidence:**",
        ]
        lines += [f"- {item}" for item in cluster.representative_problems]
        lines += ["", f"**Sources:** {', '.join(cluster.sources)}"]
        for note in cluster.notes:
            lines.append(f"- {note}")
        lines += ["", "---", ""]

    path = REPORTS / "latest.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
