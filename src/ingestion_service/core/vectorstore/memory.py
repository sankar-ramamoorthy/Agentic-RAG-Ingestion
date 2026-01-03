# src/ingestion_service/core/vectorstore/memory.py
from __future__ import annotations

from typing import Any, List

from ingestion_service.core.chunks import Chunk

"""
NON-PERSISTENT VECTOR STORE — LOCAL / TESTING ONLY.

This in-memory vector store exists to support:
- local development
- unit tests
- CI environments without PostgreSQL + pgvector

⚠ IMPORTANT:
- This store does NOT persist data across process restarts.
- This store MUST NOT be used in production.
- MS2/MS2a production vector persistence uses PgVectorStore
  (core/vectorstore/pgvector_store.py).

This implementation intentionally favors simplicity over performance
or durability.
"""


class MemoryVectorStore:
    """
    Simple in-memory vector store for MS2.

    Stores vectors and minimal metadata in a Python list.
    """

    def __init__(self) -> None:
        self._rows: list[dict[str, Any]] = []

    def persist(
        self,
        *,
        chunks: List[Chunk],
        embeddings: List[Any],
        ingestion_id: str,
    ) -> None:
        """
        Persist vectors in memory.

        This mirrors the MS2 pipeline contract and is intentionally
        incompatible with PgVectorStore's VectorRecord-based API.

        DO NOT use this outside local development or tests.
        """
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            self._rows.append(
                {
                    "ingestion_id": ingestion_id,
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": index,
                    "chunk_strategy": chunk.metadata.get("chunk_strategy"),
                    "vector": embedding,
                }
            )

    def dump(self) -> list[dict[str, Any]]:
        """
        Return a shallow copy of all stored vectors.

        Intended for debugging and assertions in tests.
        """
        return list(self._rows)
