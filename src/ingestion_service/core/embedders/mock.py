from __future__ import annotations
from typing import List

from ingestion_service.core.chunks import Chunk
from ingestion_service.core.embedders.base import BaseEmbedder


class MockEmbedder(BaseEmbedder):
    """
    Deterministic embedder for tests.
    Produces stable vectors based on chunk content length.
    """

    name = "mock"

    def embed(self, chunks: List[Chunk]) -> List[List[float]]:
        embeddings: List[List[float]] = []

        for chunk in chunks:
            length = len(str(chunk.content))
            embeddings.append(
                [
                    float(length),
                    float(length % 10),
                    1.0,
                ]
            )

        return embeddings
