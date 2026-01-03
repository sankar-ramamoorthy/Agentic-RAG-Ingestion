# src/ingestion_service/core/vectorstore/__init__.py

from ingestion_service.core.vectorstore.base import (
    VectorStore,
    VectorRecord,
    VectorMetadata,
)

from ingestion_service.core.vectorstore.pgvector_store import PgVectorStore

__all__ = [
    "VectorStore",
    "VectorRecord",
    "VectorMetadata",
    "PgVectorStore",
]
