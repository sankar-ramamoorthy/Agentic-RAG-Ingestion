import psycopg
import pytest


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """
    Hard-coded test DB URL.
    This intentionally does NOT reuse app settings.
    """
    return (
        "postgresql://ingestion_user:"
        "ingestion_pass@localhost:5433/ingestion_test"
    )


@pytest.fixture(scope="session")
def psycopg_conn(test_database_url: str):
    """
    Session-wide psycopg connection.
    """
    with psycopg.connect(test_database_url) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        yield conn


@pytest.fixture(autouse=True)
def clean_vectors_table(psycopg_conn):
    psycopg_conn.execute("DROP TABLE IF EXISTS vectors;")
    psycopg_conn.commit()
