# 🇳🇬 Nigeria Problem Radar

A 7-day research agent that continuously gathers public signals about everyday problems in Nigeria, extracts recurring pain points, clusters similar observations, and produces evidence-based opportunity reports.

## What it does

1. Collects public Google News RSS and Reddit RSS/search signals.
2. Searches across everyday-friction topics including power, connectivity, transport, food, housing, repairs, suppliers, SME finance, healthcare, education, government services, logistics, water, security and more.
3. Detects language associated with real-world friction (`can't find`, `too expensive`, `scam`, `takes too long`, `failed transaction`, `poor network`, etc.).
4. Extracts structured observations with source URL and publication time.
5. Categorizes observations and affected groups.
6. Deduplicates repeated observations.
7. Clusters semantically similar problems with TF-IDF/cosine similarity.
8. Measures evidence volume, source diversity, recurrence, pain, information gap, automation potential and monetization signals separately.
9. Generates a cumulative `reports/latest.md` research report.
10. Runs automatically through GitHub Actions every 6 hours.
11. Keeps a seven-day research window; after seven days the scheduled job stops collecting until manually restarted.

## Current design principle

**Evidence first, solutions second.** The agent must not decide what business to build. It records the problem, evidence, affected group, recurring signals and source so we can make the decision after the research window.

The scoring fields are research signals, not predictions or guarantees. A high score means the collected evidence deserves deeper investigation, not that a business will succeed.

## Zero-cost MVP

The first version does **not** require Supabase or paid AI APIs. Research data is stored as JSON in the repository and reports are committed by GitHub Actions. This makes the first seven-day experiment easy to run at ₦0.

Supabase/LLM enrichment can be added after we know the research pipeline is producing useful signals.

## Sources and ethics

Only public, non-authenticated RSS sources are used. The agent does not bypass authentication, paywalls, robots restrictions or private content. Source URLs and publication timestamps are retained for traceability. Because public feeds can contain noise, final opportunity decisions should be verified against independent sources and direct user interviews before building.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m agent.run
```

Windows:

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
