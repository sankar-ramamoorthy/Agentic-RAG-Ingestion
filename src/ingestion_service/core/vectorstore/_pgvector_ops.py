# src/ingestion_service/core/vectorstore/_pgvector_ops.py
"""
INTERNAL / FUTURE USE ONLY — NOT PART OF MS2 / MS2a WRITE PATH.

This module contains helper expressions for pgvector operations when using
SQLAlchemy ORM models (e.g., cosine distance queries).

⚠ IMPORTANT:
- This file is NOT used by the current ingestion or persistence pipeline.
- MS2/MS2a vector persistence uses raw psycopg SQL via PgVectorStore
  (core/vectorstore/pgvector_store.py).
- This module depends on the deprecated VectorEmbedding ORM model and exists
  solely as a possible future direction for ORM-based vector querying.

DO NOT:
- Import this module into ingestion pipelines
- Use this for vector writes
- Assume this code is exercised in production

Safe to ignore for MS2/MS2a.
"""

from typing import Sequence, Any

from ingestion_service.core.db.models.vector_embedding import VectorEmbedding


def cosine_distance_expr(query_vector: Sequence[float]) -> Any:
    """
    Return a SQLAlchemy expression for cosine distance against a query vector.

    This relies on pgvector's dynamically-injected SQLAlchemy operators.
    Static type checkers (Pylance / Pyright) cannot infer these methods.

    This function is intended ONLY for future ORM-based similarity queries
    and is not used in the current system.
    """
    return VectorEmbedding.embedding.cosine_distance(query_vector)
