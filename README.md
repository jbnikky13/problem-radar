# 🇳🇬 Nigeria Problem Radar

A 7-day research agent that continuously gathers public signals about everyday problems in Nigeria, extracts recurring pain points, clusters similar observations, and produces evidence-based opportunity reports.

## What it does

1. Collects public RSS/news and Reddit signals.
2. Detects language associated with real-world friction (`can't find`, `too expensive`, `scam`, `takes too long`, etc.).
3. Extracts structured observations.
4. Categorizes problems: power, connectivity, transport, food, housing, repairs, payments, business, healthcare, education, government, jobs, logistics, agriculture, security and more.
5. Deduplicates similar observations.
6. Builds recurring problem clusters.
7. Generates a daily report and cumulative `reports/latest.md`.
8. Runs automatically through GitHub Actions every 6 hours.
9. Keeps a seven-day research window; after seven days the scheduled job stops collecting until manually restarted.

## Current design principle

**Evidence first, solutions second.** The agent must not decide what business to build. It records the problem, evidence, affected group, current workaround, pain signals and source so we can make the decision after the research window.

## Zero-cost MVP

The first version does **not** require Supabase or paid AI APIs. Research data is stored as JSON in the repository and reports are committed by GitHub Actions. This makes the first seven-day experiment easy to run at ₦0.

Supabase/LLM enrichment can be added after we know the research pipeline is producing useful signals.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m agent.run
```

The Windows activation command is:

```powershell
.venv\Scripts\activate
```

## Configuration

Optional environment variables:

- `PROBLEM_RADAR_DAYS=7`
- `PROBLEM_RADAR_MAX_ITEMS_PER_SOURCE=40`
- `PROBLEM_RADAR_LOOKBACK_HOURS=48`

No API key is required for the initial collectors.

## Repository layout

```text
agent/
  __init__.py
  config.py
  models.py
  sources.py
  analyzer.py
  storage.py
  report.py
  run.py

data/
  observations.json
  clusters.json
  state.json
reports/
  latest.md
.github/workflows/
  research.yml
```

## Seven-day experiment

The agent records `started_at` in `data/state.json` on its first successful run. Every later run checks that timestamp. Once the seven-day window has elapsed, the collector exits cleanly instead of continuing to create noise.

To intentionally start a new experiment, delete `data/state.json` and run the workflow manually.

## Safety and source handling

Only public, non-authenticated sources are collected in this MVP. The agent stores source URLs and publication timestamps so observations can be traced back to their evidence. It does not attempt to bypass authentication, paywalls, robots restrictions or private content.
