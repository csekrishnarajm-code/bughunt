from app.config import normalize_database_url


def test_plain_postgres_urls_use_psycopg2():
    assert normalize_database_url("postgres://u:p@host/db") == "postgresql+psycopg2://u:p@host/db"
    assert normalize_database_url("postgresql://u:p@host/db") == "postgresql+psycopg2://u:p@host/db"


def test_neon_ssl_option_is_kept():
    url = "postgresql://u:p@ep-1.neon.tech/neondb?sslmode=require"
    assert normalize_database_url(url) == "postgresql+psycopg2://u:p@ep-1.neon.tech/neondb?sslmode=require"


def test_explicit_driver_and_sqlite_are_unchanged():
    assert normalize_database_url("postgresql+psycopg2://u:p@h/db") == "postgresql+psycopg2://u:p@h/db"
    assert normalize_database_url("sqlite:///./x.db") == "sqlite:///./x.db"
