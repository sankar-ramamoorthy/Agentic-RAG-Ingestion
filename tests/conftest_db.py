# tests/conftest_db.py
import os
import pytest
import psycopg

# Must be set in the environment before running tests
# e.g., export DATABASE_URL=postgresql://ingestion_user:ingestion_pass@postgres:5432/ingestion_test


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Return DATABASE_URL from environment."""
    return os.environ["DATABASE_URL"]


@pytest.fixture(scope="session")
def psycopg_conn(test_database_url: str):
    """Session-wide psycopg connection."""
    with psycopg.connect(test_database_url) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        yield conn


@pytest.fixture(autouse=True)
def clean_vectors_table(psycopg_conn):
    """Clean vectors table before each test."""
    psycopg_conn.execute("DROP TABLE IF EXISTS vectors;")
    psycopg_conn.commit()
