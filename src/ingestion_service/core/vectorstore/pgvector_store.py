# src/ingestion_service/core/vectorstore/pgvector_store.py

from __future__ import annotations

from typing import Sequence, Iterable, List, Any, Dict
import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from ingestion_service.core.chunks import Chunk
from ingestion_service.core.vectorstore.base import (
    VectorStore,
    VectorRecord,
    VectorMetadata,
)


class PgVectorStore(VectorStore):
    """
    PostgreSQL + pgvector-backed VectorStore.

    Production vector persistence layer for MS2a+.

    Design notes:
    - Uses raw psycopg (no ORM)
    - Schema is owned by Alembic migrations
    - Stores embeddings + chunk metadata
    - Adapter-compatible with MS2/MS2a pipeline (.persist)
    """

    SCHEMA = "ingestion_service"
    TABLE_NAME = "vectors"

    def __init__(self, dsn: str, dimension: int) -> None:
        self._dsn = dsn
        self._dimension = dimension
        self._validate_table()

    # ==========================================================
    # VectorStore interface
    # ==========================================================

    @property
    def dimension(self) -> int:
        return self._dimension

    def add(self, records: Iterable[VectorRecord]) -> None:
        insert_sql = sql.SQL(
            """
            INSERT INTO {schema}.{table}
                (vector,
                 ingestion_id,
                 chunk_id,
                 chunk_index,
                 chunk_strategy,
                 chunk_text,
                 source_metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        ).format(
            schema=sql.Identifier(self.SCHEMA),
            table=sql.Identifier(self.TABLE_NAME),
        )

        with psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                for record in records:
                    cur.execute(
                        insert_sql,
                        (
                            record.vector,
                            record.metadata.ingestion_id,
                            record.metadata.chunk_id,
                            record.metadata.chunk_index,
                            record.metadata.chunk_strategy,
                            record.metadata.chunk_text,
                            Jsonb(record.metadata.source_metadata or {}),  # safe JSONB
                        ),
                    )

    def similarity_search(
        self,
        query_vector: Sequence[float],
        k: int,
    ) -> List[VectorRecord]:
        search_sql = sql.SQL(
            """
            SELECT
                vector,
                ingestion_id,
                chunk_id,
                chunk_index,
                chunk_strategy,
                chunk_text,
                source_metadata
            FROM {schema}.{table}
            ORDER BY vector <-> (%s::vector)
            LIMIT %s
            """
        ).format(
            schema=sql.Identifier(self.SCHEMA),
            table=sql.Identifier(self.TABLE_NAME),
        )

        results: List[VectorRecord] = []

        with psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(search_sql, (query_vector, k))
                for row in cur.fetchall():
                    (
                        vector,
                        ingestion_id,
                        chunk_id,
                        chunk_index,
                        chunk_strategy,
                        chunk_text,
                        source_metadata,
                    ) = row

                    metadata = VectorMetadata(
                        ingestion_id=ingestion_id,
                        chunk_id=chunk_id,
                        chunk_index=chunk_index,
                        chunk_strategy=chunk_strategy,
                        chunk_text=chunk_text,
                        source_metadata=source_metadata,
                    )

                    results.append(VectorRecord(vector=vector, metadata=metadata))

        return results

    def delete_by_ingestion_id(self, ingestion_id: str) -> None:
        delete_sql = sql.SQL(
            """
            DELETE FROM {schema}.{table}
            WHERE ingestion_id = %s
            """
        ).format(
            schema=sql.Identifier(self.SCHEMA),
            table=sql.Identifier(self.TABLE_NAME),
        )

        with psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(delete_sql, (ingestion_id,))

    def reset(self) -> None:
        truncate_sql = sql.SQL(
            """
            TRUNCATE TABLE {schema}.{table}
            """
        ).format(
            schema=sql.Identifier(self.SCHEMA),
            table=sql.Identifier(self.TABLE_NAME),
        )

        with psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(truncate_sql)

    # ==========================================================
    # MS2 / MS2a pipeline adapter
    # ==========================================================

    def persist(
        self,
        *,
        chunks: List[Chunk],
        embeddings: List[Any],
        ingestion_id: str,
        source_metadata: Dict[str, Any] | None = None,
    ) -> None:
        """
        Adapter for MS2/MS2a pipeline contract.

        Converts Chunk + embedding pairs into VectorRecords
        and persists them using the VectorStore API.
        """
        records: List[VectorRecord] = []

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            record = VectorRecord(
                vector=embedding,
                metadata=VectorMetadata(
                    ingestion_id=ingestion_id,
                    chunk_id=chunk.chunk_id,
                    chunk_index=index,
                    chunk_strategy=chunk.metadata.get("chunk_strategy", "unknown"),
                    chunk_text=str(chunk.content),
                    source_metadata=source_metadata or {},
                ),
            )
            records.append(record)

        self.add(records)

    # ==========================================================
    # Internal
    # ==========================================================

    def _validate_table(self) -> None:
        """
        Fail-fast schema validation.

        Ensures the vectors table exists and has a pgvector column.
        """
        probe_sql = sql.SQL(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = {schema}
              AND table_name = {table}
              AND column_name = 'vector'
              AND udt_name = 'vector'
            """
        ).format(
            schema=sql.Literal(self.SCHEMA),
            table=sql.Literal(self.TABLE_NAME),
        )

        try:
            with psycopg.connect(self._dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(probe_sql)
                    if cur.rowcount == 0:
                        raise RuntimeError("pgvector column not found")
        except Exception as exc:
            raise RuntimeError(
                f"PgVectorStore schema validation failed: "
                f"table '{self.SCHEMA}.{self.TABLE_NAME}' missing or incompatible. "
                f"Have you run Alembic migrations?"
            ) from exc
