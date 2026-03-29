"""
Knowledge store — loads LPI data into memory and provides keyword search.
Ported from LPI MCP Server knowledge-store.ts.
"""
import json
import os
from dataclasses import dataclass

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@dataclass
class SearchResult:
    id: str
    title: str
    content: str
    tags: list[str]
    source: str
    score: float
    tier: str


class KnowledgeStore:
    def __init__(self):
        self.entries: list[dict] = []
        self.case_studies: list[dict] = []
        self.smile: dict = {}
        self._load()

    def _load(self):
        with open(os.path.join(DATA_DIR, "knowledge-base.json")) as f:
            self.entries = json.load(f)
        with open(os.path.join(DATA_DIR, "case-studies.json")) as f:
            self.case_studies = json.load(f)
        with open(os.path.join(DATA_DIR, "smile-framework.json")) as f:
            self.smile = json.load(f)

    def search(self, query: str, limit: int = 5, include_paid: bool = False) -> list[SearchResult]:
        # Clean query: lowercase, strip punctuation for matching
        import re
        clean_query = re.sub(r'[^\w\s]', '', query.lower())
        terms = clean_query.split()
        if not terms:
            return []

        # Detect beginner intent — boost intro content only when no specific topic terms
        beginner_signals = {"what", "how", "start", "begin", "getting", "started", "basics", "new", "explain", "introduction", "necessary"}
        topic_signals = {"smile", "edge", "interoperability", "ontology", "ant", "mim", "lean", "mvt", "sustainability", "energy", "building", "buildings", "maritime", "methodology", "phase", "phases"}
        has_beginner_words = len(beginner_signals.intersection(terms)) >= 1
        has_topic_words = len(topic_signals.intersection(terms)) >= 1
        is_beginner = has_beginner_words and not has_topic_words

        scored: list[tuple[dict, float]] = []

        for entry in self.entries:
            if not include_paid and entry.get("tier") == "paid":
                continue
            if entry.get("visibility") != "public":
                continue
            score = self._score_entry(entry, terms)
            # Boost beginner-friendly content only for truly introductory questions
            if is_beginner and any(t in entry.get("tags", []) for t in ["beginner", "introduction", "getting-started"]):
                score += 10.0
            if score > 0:
                scored.append((entry, score))

        # Also search case studies (free tier only)
        for cs in self.case_studies:
            if not include_paid and cs.get("tier") == "paid":
                continue
            score = self._score_case_study(cs, terms)
            if score > 0:
                scored.append((cs, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for entry, score in scored[:limit]:
            results.append(SearchResult(
                id=entry.get("id", ""),
                title=entry.get("title", ""),
                content=entry.get("content") or entry.get("summary", ""),
                tags=entry.get("tags", entry.get("smilePhases", [])),
                source=entry.get("source", entry.get("industry", "")),
                score=score,
                tier=entry.get("tier", "free"),
            ))

        return results

    # Common words that shouldn't contribute to title/content matching
    STOP_WORDS = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                  "do", "does", "did", "have", "has", "had", "it", "its",
                  "to", "of", "in", "for", "on", "with", "at", "by", "from",
                  "and", "or", "but", "not", "no", "this", "that", "these",
                  "i", "me", "my", "we", "our", "you", "your", "they", "them",
                  "even", "also", "just", "very", "so", "too"}

    def _score_entry(self, entry: dict, terms: list[str]) -> float:
        score = 0.0
        title = entry.get("title", "").lower()
        content = entry.get("content", "").lower()
        tags = " ".join(entry.get("tags", [])).lower()

        for term in terms:
            if term in self.STOP_WORDS:
                continue
            if term in title:
                score += 3.0
            if term in tags:
                score += 2.0
            if term in content:
                score += 1.0

        return score

    def _score_case_study(self, cs: dict, terms: list[str]) -> float:
        score = 0.0
        title = cs.get("title", "").lower()
        challenge = cs.get("challenge", "").lower()
        approach = cs.get("approach", "").lower()
        outcome = cs.get("outcome", "").lower()
        industry = cs.get("industry", "").lower()

        for term in terms:
            if term in title:
                score += 3.0
            if term in industry:
                score += 2.0
            if term in challenge or term in approach or term in outcome:
                score += 1.0

        return score

    def get_smile_overview(self) -> dict:
        return {
            "methodology": self.smile.get("methodology", {}),
            "phases": [
                {"name": p["name"], "order": p["order"], "description": p["description"], "duration": p["duration"]}
                for p in self.smile.get("phases", [])
            ],
            "perspectives": self.smile.get("perspectives", []),
            "aiJourney": self.smile.get("aiJourney", []),
        }

    def get_phase_detail(self, phase_id: str) -> dict | None:
        for phase in self.smile.get("phases", []):
            if phase["id"] == phase_id:
                return phase
        return None

    def has_paid_matches(self, query: str) -> bool:
        """Check if query would match paid-tier content (for CTA triggers)."""
        terms = query.lower().split()
        for entry in self.entries:
            if entry.get("tier") == "paid":
                if self._score_entry(entry, terms) > 0:
                    return True
        for cs in self.case_studies:
            if cs.get("tier") == "paid":
                if self._score_case_study(cs, terms) > 0:
                    return True
        return False


# Singleton
store = KnowledgeStore()
