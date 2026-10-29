import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from . import config


class RateLimiter:
    """Small in-memory sliding-window limiter (one process, fine for a demo)."""

    def __init__(self, window_seconds: int = 60):
        self.window = window_seconds
        self.hits = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key: str, limit: int) -> bool:
        now = time.monotonic()
        with self.lock:
            queue = self.hits[key]
            while queue and now - queue[0] > self.window:
                queue.popleft()
            if len(queue) >= limit:
                return False
            queue.append(now)
            return True

    def reset(self):
        with self.lock:
            self.hits.clear()


limiter = RateLimiter()


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(request: Request):
    if not limiter.allow(client_ip(request), config.RATE_LIMIT_PER_MIN):
        raise HTTPException(429, "Too many games started. Please wait a minute and try again.")
