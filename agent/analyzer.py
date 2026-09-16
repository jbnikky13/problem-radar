from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from urllib.parse import urlparse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import Cluster, Observation
from .sources import PROBLEM_PATTERNS

CATEGORIES = {
    "power": ["electricity", "power", "generator", "diesel", "fuel", "inverter", "solar", "nepa", "phcn"],
    "connectivity": ["internet", "data", "network", "wifi", "broadband", "airtel", "mtn", "glo", "9mobile"],
    "transport": ["transport", "bus", "taxi", "fare", "traffic", "commute", "road", "bolt", "uber"],
    "food": ["food", "rice", "beans", "tomato", "market", "grocery", "price", "cooking"],
    "housing": ["rent", "house", "landlord", "property", "apartment", "housing", "estate"],
    "repairs": ["repair", "technician", "plumber", "electrician", "mechanic", "artisan", "ac", "generator"],
    "payments": ["payment", "transfer", "pos", "bank", "invoice", "reconciliation", "refund", "charge"],
    "business": ["business", "customer", "sales", "inventory", "profit", "expense", "supplier", "wholesale", "accounting", "merchant"],
    "healthcare": ["hospital", "doctor", "clinic", "medicine", "drug", "health", "patient", "pharmacy"],
    "education": ["school", "student", "teacher", "tuition", "exam", "university", "education"],
    "government": ["government", "cac", "tax", "passport", "license", "registration", "agency", "document"],
    "jobs": ["job", "work", "employment", "hiring", "salary", "career", "cv", "unemployment"],
    "logistics": ["delivery", "package", "shipping", "courier", "logistics", "dispatch", "warehouse"],
    "agriculture": ["farmer", "farm", "crop", "harvest", "fertilizer", "agriculture", "produce"],
    "security": ["security", "scam", "fraud", "theft", "robbery", "fake", "unsafe"],
    "water": ["water", "borehole", "tanker", "well", "wastewater"],
}

GROUPS = {
    "consumers": ["consumer", "people", "customer", "household", "residents"],
    "students": ["student", "school", "university", "campus"],
    "workers": ["worker", "employee", "salary", "commute", "job"],
    "smes": ["business", "shop", "seller", "merchant", "vendor", "restaurant", "store"],
    "parents": ["parent", "child", "school fees"],
    "drivers": ["driver", "transport", "vehicle", "dispatch"],
}

HIGH_TRUST_DOMAINS = {"nigerianstat.gov.ng", "cbn.gov.ng", "worldbank.org", "who.int", "unicef.org", "fccpc.gov.ng", "nerc.gov.ng", "gov.ng"}
NEWS_DOMAINS = {"punchng.com", "guardian.ng", "vanguardngr.com", "premiumtimesng.com", "businessday.ng", "thisdaylive.com", "nairametrics.com"}


def _signals(text: str) -> tuple[list[str], float]:
    lower = text.lower()
    found, score = [], 0.0
    for phrase, weight in PROBLEM_PATTERNS:
        if phrase in lower:
            found.append(phrase)
            score += weight
    return found, min(10.0, score)


def _category(text: str) -> str:
    lower = text.lower()
    scores = {name: sum(lower.count(term) for term in terms) for name, terms in CATEGORIES.items()}
    best, value = max(scores.items(), key=lambda x: x[1])
    return best if value else "other"


def _groups(text: str) -> list[str]:
    lower = text.lower()
    return [name for name, terms in GROUPS.items() if any(term in lower for term in terms)] or ["general_public"]


def _domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower().split(":")[0]
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


def _source_quality(source: str, url: str) -> tuple[str, float]:
    domain = _domain(url)
    if any(domain == d or domain.endswith("." + d) for d in HIGH_TRUST_DOMAINS):
        return "official_or_institutional", 9.5
    if any(domain == d or domain.endswith("." + d) for d in NEWS_DOMAINS):
        return "established_news", 8.0
    if "reddit.com" in domain:
        return "community", 5.5
    if "google.com" in domain:
        return "search_aggregator", 4.5
    return "public_web", 5.0


def extract(raw: list[dict]) -> list[Observation]:
    observations = []
    for item in raw:
        signals, pain = _signals(item["text"])
        if pain < 1.5:
            continue
        category = _category(item["text"])
        source_type, credibility = _source_quality(item.get("source", ""), item.get("url", ""))
        evidence_quality = round(min(10.0, credibility * 0.65 + min(10.0, len(signals) * 0.8) * 0.35), 2)
        observations.append(Observation(
            id=item["id"], title=item["title"], text=item["text"], source=item["source"],
            url=item["url"], published_at=item["published_at"], collected_at=item["collected_at"],
            category=category, signals=signals, affected_groups=_groups(item["text"]),
            evidence_score=min(10.0, 3.0 + len(signals) * 0.7), pain_score=pain,
            tags=signals + [category], source_domain=_domain(item.get("url", "")),
            source_type=source_type, source_credibility=credibility, evidence_quality=evidence_quality,
        ))
    return observations


def cluster(observations: list[Observation]) -> list[Cluster]:
    if not observations:
        return []
    texts = [f"{o.category} {o.title} {o.text}" for o in observations]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(texts)
    similarity = cosine_similarity(matrix)
    parent = list(range(len(observations)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(len(observations)):
        for j in range(i + 1, len(observations)):
            if observations[i].category == observations[j].category and similarity[i, j] >= 0.32:
                union(i, j)

    groups: dict[int, list[Observation]] = defaultdict(list)
    for idx, obs in enumerate(observations):
        groups[find(idx)].append(obs)

    clusters = []
    for members in sorted(groups.values(), key=len, reverse=True):
        category = Counter(o.category for o in members).most_common(1)[0][0]
        phrases = Counter(signal for o in members for signal in o.signals)
        representative = [o.title for o in sorted(members, key=lambda x: x.pain_score, reverse=True)[:5]]
        source_names = sorted({o.source for o in members})
        source_domains = sorted({o.source_domain for o in members if o.source_domain})
        source_count = len(source_domains)
        unique_urls = len({o.url for o in members})
        recurrence = min(10.0, 2.0 + len(members) * 1.1)
        avg_quality = sum(o.evidence_quality for o in members) / len(members)
        evidence = min(10.0, 1.5 + len(members) * 0.7 + source_count * 1.0 + avg_quality * 0.15)
        pain = sum(o.pain_score for o in members) / len(members)
        gap_terms = {"can't find", "cannot find", "unavailable", "looking for", "how do i", "recommend", "where can i", "how can i"}
        gap = min(10.0, 2.0 + sum(1 for p in phrases if p in gap_terms) * 1.2 + source_count * 0.8)
        automation = min(10.0, 2.5 + (2.0 if category in {"business", "payments", "logistics", "jobs", "government"} else 0) + len(members) * 0.35)
        monetization = min(10.0, 2.0 + (2.5 if category in {"business", "payments", "logistics", "housing", "jobs", "repairs"} else 0) + len(members) * 0.35)
        source_diversity = min(10.0, 2.0 + source_count * 1.5)
        verification = min(10.0, avg_quality * 0.55 + source_diversity * 0.45)
        existing_solution_terms = ["app", "platform", "website", "marketplace", "service", "already", "available", "directory"]
        existing_signal = min(10.0, sum(1 for o in members if any(term in o.text.lower() for term in existing_solution_terms)) / max(1, len(members)) * 10.0)
        confidence = "high" if verification >= 7.5 and source_count >= 3 else "medium" if verification >= 5.5 or source_count >= 2 else "low"
        cluster_id = sha256("|".join(sorted(o.id for o in members)).encode()).hexdigest()[:12]
        clusters.append(Cluster(
            id=cluster_id, title=representative[0][:120], category=category,
            observation_ids=[o.id for o in members], observation_count=len(members),
            evidence_score=round(evidence, 2), pain_score=round(pain, 2),
            recurrence_score=round(recurrence, 2), information_gap_score=round(gap, 2),
            automation_score=round(automation, 2), monetization_signal_score=round(monetization, 2),
            source_diversity_score=round(source_diversity, 2), verification_score=round(verification, 2),
            evidence_confidence=confidence, existing_solution_signal=round(existing_signal, 2),
            representative_problems=representative, sources=source_names, source_domains=source_domains,
            notes=[
                f"Common signals: {', '.join(p for p, _ in phrases.most_common(5))}",
                f"Independent source domains: {source_count}; unique observations: {unique_urls}",
                f"Average source/evidence quality: {avg_quality:.1f}/10; verification confidence: {confidence}",
                f"Existing-solution language signal: {existing_signal:.1f}/10 (not a market-size estimate)",
            ],
        ))
    return clusters
