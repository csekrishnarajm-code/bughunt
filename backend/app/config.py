import os

TIME_LIMIT_SECONDS = 45      # time allowed per bug
GRACE_SECONDS = 2            # network delay allowance
MIN_ROUNDS = 3
MAX_ROUNDS = 10
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "20"))
LEADERBOARD_MAX = 50
NAME_PATTERN = r"^[A-Za-z0-9 _.\-]{1,20}$"


def normalize_database_url(url: str) -> str:
    """Make any common PostgreSQL URL work with the psycopg2 driver we install.

    Neon, Render and Heroku give postgres:// or postgresql:// URLs without a driver name,
    and newer SQLAlchemy versions would pick a different driver for those.
    """
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg2://" + url[len(prefix):]
    return url


def database_url() -> str:
    return normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./bughunt.db"))
