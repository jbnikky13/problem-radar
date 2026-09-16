from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

import feedparser
import requests

from .config import CONFIG


SEARCH_QUERIES = [
    'Nigeria "can’t find" OR "can't find" OR "cannot find"',
    'Nigeria "too expensive" OR "costly" OR "price increase"',
    'Nigeria "takes too long" OR "waste time" OR "long queue"',
    'Nigeria scam OR fraud OR fake OR counterfeit',
    'Nigeria "no electricity" OR "power outage" OR generator OR "estimated bill"',
    'Nigeria data internet network expensive OR "poor network" OR "dropped calls"',
    'Nigeria transport fare bus traffic commute OR "transport cost"',
    'Nigeria rent landlord house property scam OR "house hunting"',
    'Nigeria repair technician artisan plumber electrician OR mechanic',
    'Nigeria supplier price wholesale business OR "where to buy"',
    'Nigeria small business payment accounting inventory OR "cash flow"',
    'Nigeria healthcare hospital medicine availability OR pharmacy',
    'Nigeria job application hiring unemployment OR "job search"',
    'Nigeria government service registration documentation OR passport',
    'Nigeria delivery logistics package courier OR dispatch',
    'Nigeria food prices market shopping OR groceries',
    'Nigeria school fees education textbook parent',
    'Nigeria water supply borehole tanker water vendor',
    'Nigeria security theft fraud consumer protection complaint',
    'Nigeria POS failed transaction bank transfer reversal charge',
    'Nigeria solar inverter battery technician maintenance',
    'Nigeria small business customer debt invoice reconciliation',
]

RSS_FEEDS = {
    "Google News": [
        "https://news.google.com/rss/search?q={query}&hl=en-NG&gl=NG&ceid=NG:en",
    ],
    "Reddit Nigeria": [
        "https://www.reddit.com/r/Nigeria/new/.rss",
        "https://www.reddit.com/r/NigerianFluency/new/.rss",
        "https://www.reddit.com/r/NigerianBusiness/new/.rss",
    ],
    "Reddit Search": [
        "https://www.reddit.com/search.rss?q={query}&sort=new&t=week",
    ],
}

PROBLEM_PATTERNS = [
    ("can't find", 3.0), ("cannot find", 3.0), ("can't get", 3.0),
    ("cannot get", 3.0), ("how do i", 2.0), ("how can i", 2.0),
    ("too expensive", 3.0), ("costly", 2.0), ("expensive", 1.5),
    ("scam", 3.0), ("fraud", 3.0), ("fake", 2.5), ("counterfeit", 3.0),
    ("waste time", 2.5), ("takes too long", 2.5), ("long queue", 2.0),
    ("unavailable", 2.0), ("no electricity", 3.0), ("power outage", 2.5),
    ("poor network", 2.5), ("dropped calls", 2.0), ("failed transaction", 2.5),
    ("reversal", 2.0), ("complain", 1.5), ("complaint", 1.5),
    ("problem", 1.5), ("issue", 1.0), ("frustrat", 2.5), ("difficult", 2.0),
    ("hard to", 2.0), ("looking for", 1.5), ("recommend", 1.0),
    ("overcharged", 2.5), ("lost money", 3.0), ("charged twice", 3.0),
    ("delayed", 2.0), ("delay", 1.5), ("not working", 2.0),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _published(entry) -> str:
    raw = entry.get("published") or entry.get("updated")
    if not raw:
        return _now()
    try:
        return parsedate_to_datetime(raw).astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError):
        return str(raw)


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def _id(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()[:16]


def _fetch(url: str):
    headers = {"User-Agent": CONFIG.user_agent}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return feedparser.parse(response.content)


def _append_feed(items: list[dict], seen: set[str], feed_name: str, feed_url: str, query: str | None = None) -> None:
    url = feed_url.format(query=quote_plus(query)) if "{query}" in feed_url and query else feed_url
    try:
        feed = _fetch(url)
    except Exception as exc:
        print(f"[source] {feed_name} failed: {exc}")
        return
    for entry in feed.entries[: CONFIG.max_items_per_source]:
        title = _clean(entry.get("title", ""))
        summary = _clean(entry.get("summary", ""))
        link = entry.get("link", "")
        key = _id(link, title)
        if not title or key in seen:
            continue
        seen.add(key)
        items.append({
            "id": key,
            "title": title,
            "text": f"{title}. {summary}".strip(),
            "source": feed_name,
            "url": link,
            "published_at": _published(entry),
            "collected_at": _now(),
        })


def collect() -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()

    for query in SEARCH_QUERIES:
        _append_feed(items, seen, "Google News", RSS_FEEDS["Google News"][0], query)

    for feed_url in RSS_FEEDS["Reddit Nigeria"]:
        _append_feed(items, seen, "Reddit Nigeria", feed_url)

    for query in SEARCH_QUERIES[:12]:
        _append_feed(items, seen, "Reddit Search", RSS_FEEDS["Reddit Search"][0], query)

    return items
