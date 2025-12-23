# src/ingestion_service/core/pipeline.py

from __future__ import annotations
from typing import Any, Optional
from ingestion_service.core.chunks import Chunk
from ingestion_service.core.chunkers.base import BaseChunker
from ingestion_service.core.chunkers.selector import ChunkerFactory


class IngestionPipeline:
    def __init__(
        self,
        *,
        validator,
        chunker: Optional[BaseChunker] = None,
        embedder,
        vector_store,
    ) -> None:
        """
        Initialize the pipeline with injected collaborators.
        If chunker is None, a dynamic chunker will be selected at runtime.
        """
        self._validator = validator
        self._chunker = chunker
        self._embedder = embedder
        self._vector_store = vector_store

    def run(self, *, text: str, ingestion_id: str) -> None:
        """
        Execute the ingestion pipeline:
        1. Validate input
        2. Chunk into pieces
        3. Generate embeddings
        4. Persist chunks + embeddings
        """
        self._validate(text)
        chunks = self._chunk(text)
        embeddings = self._embed(chunks)
        self._persist(chunks, embeddings, ingestion_id)

    # ---- pipeline steps ----

    def _validate(self, text: str) -> None:
        self._validator.validate(text)

    def _chunk(self, text: str) -> list[Chunk]:
        """
        Chunk text using either the provided chunker or a dynamically selected one.
        Returns a list of Chunk objects with chunking metadata.
        """
        if self._chunker is None:
            # Dynamically select strategy (LLM or heuristic)
            selected_chunker, chunker_params = ChunkerFactory.choose_strategy(text)
        else:
            selected_chunker = self._chunker
            chunker_params = {}

        chunks: list[Chunk] = selected_chunker.chunk(text, **chunker_params)

        # Record chunking strategy in metadata
        for chunk in chunks:
            chunk.metadata["chunking_strategy"] = getattr(
                selected_chunker, "name", "unknown"
            )
            chunk.metadata["chunker_params"] = chunker_params

        return chunks

    def _embed(self, chunks: list[Chunk]) -> list[Any]:
        """
        Produce embeddings for a list of chunks.
        """
        return self._embedder.embed(chunks)

    def _persist(
        self, chunks: list[Chunk], embeddings: list[Any], ingestion_id: str
    ) -> None:
        """
        Persist chunks and embeddings to the vector store.
        """
        self._vector_store.persist(
            chunks=chunks,
            embeddings=embeddings,
            ingestion_id=ingestion_id,
        )
