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
            + c.automation_score + c.monetization_signal_score + c.verification_score
        ),
        reverse=True,
    )
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        "# 🇳🇬 Nigeria Problem Radar — Evidence Intelligence",
        "",
        f"Generated: `{now}`",
        f"Research status: **{'ACTIVE' if active else 'COMPLETE'}**",
        f"Unique observations collected: **{observation_count}**",
        "",
        "> Evidence report only. Scores are research signals, not predictions, rankings of people, or automatic business recommendations.",
        "> A high signal means a problem deserves investigation; it does not prove market size, profitability, or product-market fit.",
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
            f"**Pain signal:** {cluster.pain_score}/10  ",
            f"**Recurrence:** {cluster.recurrence_score}/10  ",
            f"**Information gap:** {cluster.information_gap_score}/10  ",
            f"**Automation signal:** {cluster.automation_score}/10  ",
            f"**Monetization signal:** {cluster.monetization_signal_score}/10  ",
            f"**Source diversity:** {cluster.source_diversity_score}/10  ",
            f"**Verification:** {cluster.verification_score}/10  ",
            f"**Evidence confidence:** **{cluster.evidence_confidence}**  ",
            f"**Existing-solution language:** {cluster.existing_solution_signal}/10",
            "",
            "**Representative evidence:**",
        ]
        lines += [f"- {item}" for item in cluster.representative_problems]
        lines += ["", f"**Source domains:** {', '.join(cluster.source_domains) or 'unknown'}"]
        for note in cluster.notes:
            lines.append(f"- {note}")
        lines += ["", "---", ""]

    path = REPORTS / "latest.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
