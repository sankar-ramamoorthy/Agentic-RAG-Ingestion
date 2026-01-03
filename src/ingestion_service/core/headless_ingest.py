from __future__ import annotations
from typing import List, Optional

from ingestion_service.core.pipeline import IngestionPipeline
from ingestion_service.core.vectorstore.base import VectorRecord, VectorMetadata


class HeadlessIngestor:
    """
    Runs a headless ingestion pipeline (no FastAPI involved).
    """

    def __init__(self, pipeline: IngestionPipeline):
        self.pipeline = pipeline

    def ingest_text(
        self,
        text: str,
        ingestion_id: str,
        source_metadata: Optional[dict] = None,
    ) -> None:
        chunks = self.pipeline._chunk(text)
        embeddings = self.pipeline._embed(chunks)

        vector_records: List[VectorRecord] = []

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_records.append(
                VectorRecord(
                    vector=embedding,
                    metadata=VectorMetadata(
                        ingestion_id=ingestion_id,
                        chunk_id=chunk.chunk_id,
                        chunk_index=index,
                        chunk_strategy=chunk.metadata.get("chunk_strategy", "unknown"),
                        chunk_text=str(chunk.content),
                        source_metadata=source_metadata,
                    ),
                )
            )

        self.pipeline._vector_store.add(vector_records)
