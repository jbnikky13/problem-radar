from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    research_days: int = int(os.getenv("PROBLEM_RADAR_DAYS", "7"))
    max_items_per_source: int = int(os.getenv("PROBLEM_RADAR_MAX_ITEMS_PER_SOURCE", "40"))
    lookback_hours: int = int(os.getenv("PROBLEM_RADAR_LOOKBACK_HOURS", "48"))
    user_agent: str = "NigeriaProblemRadar/0.1 (+https://github.com/jbnikky13/problem-radar)"


CONFIG = Config()
