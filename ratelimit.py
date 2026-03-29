"""
Simple in-memory rate limiter for Vercel serverless.

Note: On Vercel, each invocation may be a fresh instance, so this only
protects against burst abuse within a single instance lifetime. For
persistent rate limiting, use an external store (Redis, Upstash).
"""
import time
import threading
from collections import defaultdict
from fastapi import Request, HTTPException


_lock = threading.Lock()
_requests: dict[str, list[float]] = defaultdict(list)

# Config
MAX_REQUESTS = 30  # per window
WINDOW_SECONDS = 60


def check_rate_limit(request: Request) -> None:
    """Raise 429 if client exceeds rate limit."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - WINDOW_SECONDS

    with _lock:
        # Prune old entries
        _requests[client_ip] = [t for t in _requests[client_ip] if t > window_start]

        if len(_requests[client_ip]) >= MAX_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait a moment.",
            )

        _requests[client_ip].append(now)
