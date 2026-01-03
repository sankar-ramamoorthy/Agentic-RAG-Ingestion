from __future__ import annotations

import asyncio
from typing import Optional

from ingestion_service.core.pipeline import IngestionPipeline


class AsyncIngestionRunner:
    """
    Async wrapper around the synchronous IngestionPipeline.

    MS2a MVP goal:
    - non-blocking FastAPI ingestion
    - reuse existing pipeline unchanged
    """

    def __init__(self, pipeline: IngestionPipeline):
        self._pipeline = pipeline

    async def ingest(
        self,
        *,
        text: str,
        ingestion_id: str,
        source_metadata: Optional[dict] = None,
    ) -> None:
        loop = asyncio.get_running_loop()

        await loop.run_in_executor(
            None,
            self._pipeline._vector_store.persist,
            self._pipeline._chunk(text),
            self._pipeline._embed(self._pipeline._chunk(text)),
            ingestion_id,
            source_metadata,
        )
