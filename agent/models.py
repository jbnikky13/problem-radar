from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Observation:
    id: str
    title: str
    text: str
    source: str
    url: str
    published_at: str
    collected_at: str
    category: str
    signals: list[str] = field(default_factory=list)
    affected_groups: list[str] = field(default_factory=list)
    location: str = "Nigeria"
    evidence_score: float = 0.0
    pain_score: float = 0.0
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Cluster:
    id: str
    title: str
    category: str
    observation_ids: list[str]
    observation_count: int
    evidence_score: float
    pain_score: float
    recurrence_score: float
    information_gap_score: float
    automation_score: float
    monetization_signal_score: float
    representative_problems: list[str]
    sources: list[str]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
