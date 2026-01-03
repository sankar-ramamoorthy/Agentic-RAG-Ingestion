from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Sequence, List


@dataclass(frozen=True)
class VectorMetadata:
    ingestion_id: str
    chunk_id: str
    chunk_index: int
    chunk_strategy: str
    chunk_text: str
    source_metadata: dict | None


@dataclass(frozen=True)
class VectorRecord:
    vector: Sequence[float]
    metadata: VectorMetadata


class VectorStore(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int: ...

    @abstractmethod
    def add(self, records: Iterable[VectorRecord]) -> None: ...

    @abstractmethod
    def similarity_search(
        self,
        query_vector: Sequence[float],
        k: int,
    ) -> List[VectorRecord]: ...

    @abstractmethod
    def delete_by_ingestion_id(self, ingestion_id: str) -> None: ...
