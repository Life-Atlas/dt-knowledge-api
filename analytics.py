"""
Simple in-memory analytics for tracking chat and SPIN usage.
Resets on each Vercel cold start — for patterns, not exact counts.
For persistent analytics, swap with a proper store later.
"""
import threading
from collections import defaultdict

_lock = threading.Lock()
_counters: dict[str, int] = defaultdict(int)
_spin_completions: list[dict] = []

MAX_STORED = 100  # Keep last N SPIN completions in memory


def track_event(event: str) -> None:
    """Increment a counter for an event type."""
    with _lock:
        _counters[event] += 1


def track_spin_completion(answers: dict, product_id: str) -> None:
    """Record a SPIN completion with answers and recommended product."""
    with _lock:
        _counters["spin_complete"] += 1
        _spin_completions.append({
            "answers": answers,
            "product": product_id,
        })
        # Keep only last N
        if len(_spin_completions) > MAX_STORED:
            _spin_completions.pop(0)


def get_stats() -> dict:
    """Return current analytics snapshot."""
    with _lock:
        return {
            "counters": dict(_counters),
            "spin_completions": len(_spin_completions),
            "recent_products": [s["product"] for s in _spin_completions[-10:]],
        }
