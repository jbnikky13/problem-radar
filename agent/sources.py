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
    "Nigeria \"can't find\" OR \"cannot find\"",
    "Nigeria \"too expensive\" OR \"expensive\"",
    "Nigeria \"takes too long\" OR \"waste time\"",
    "Nigeria scam OR fraud OR fake",
    "Nigeria \"no electricity\" OR \"power outage\" OR generator",
    "Nigeria data internet network expensive",
    "Nigeria transport fare bus traffic commute",
    "Nigeria rent landlord house property scam",
    "Nigeria repair technician artisan plumber electrician",
    "Nigeria supplier price wholesale business",
    "Nigeria small business payment accounting inventory",
    "Nigeria healthcare hospital medicine availability",
    "Nigeria job application hiring unemployment",
    "Nigeria government service registration documentation",
    "Nigeria delivery logistics package",
    "Nigeria food prices market shopping",
]

RSS_FEEDS = {
    "Google News": [
        "https://news.google.com/rss/search?q={query}&hl=en-NG&gl=NG&ceid=NG:en",
    ],
    "Reddit Nigeria": [
        "https://www.reddit.com/r/Nigeria/new/.rss",
        "https://www.reddit.com/r/NigerianFluency/new/.rss",
    ],
}

PROBLEM_PATTERNS = [
    ("can't find", 3.0),
    ("cannot find", 3.0),
    ("can't get", 3.0),
    ("cannot get", 3.0),
    ("how do i", 2.0),
    ("how can i", 2.0),
    ("too expensive", 3.0),
    ("expensive", 1.5),
    ("scam", 3.0),
    ("fraud", 3.0),
    ("fake", 2.5),
    ("waste time", 2.5),
    ("takes too long", 2.5),
    ("unavailable", 2.0),
    ("no electricity", 3.0),
    ("power outage", 2.5),
    ("complain", 1.5),
    ("problem", 1.5),
    ("issue", 1.0),
    ("frustrat", 2.5),
    ("difficult", 2.0),
    ("hard to", 2.0),
    ("looking for", 1.5),
    ("recommend", 1.0),
    ("overcharged", 2.5),
    ("lost money", 3.0),
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


def collect() -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()

    for query in SEARCH_QUERIES:
        url = RSS_FEEDS["Google News"][0].format(query=quote_plus(query))
        try:
            feed = _fetch(url)
        except Exception as exc:
            print(f"[source] Google News failed: {exc}")
            continue
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
                "source": "Google News",
                "url": link,
                "published_at": _published(entry),
                "collected_at": _now(),
            })

    for feed_url in RSS_FEEDS["Reddit Nigeria"]:
        try:
            feed = _fetch(feed_url)
        except Exception as exc:
            print(f"[source] Reddit failed: {exc}")
            continue
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
                "source": "Reddit Nigeria",
                "url": link,
                "published_at": _published(entry),
                "collected_at": _now(),
            })

    return items
