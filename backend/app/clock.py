from datetime import datetime, timezone


def now() -> datetime:
    """Current UTC time. Tests replace this to control the clock."""
    return datetime.now(timezone.utc)
