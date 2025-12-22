# tests/test_db_operations.py (complete clean file)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ingestion_service.core.config import get_settings
from ingestion_service.core.models import IngestionRequest

engine = create_engine(get_settings().DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_insert_fetch_row():
    test_uuid = "123e4567-e89b-12d3-a456-426614174000"
    session = Session()
    new_ingestion = IngestionRequest(
        ingestion_id=test_uuid,
        source_type="test_source",
        ingestion_metadata={"key": "value"},
        status="pending",
    )
    session.add(new_ingestion)
    session.commit()
    fetched_row = (
        session.query(IngestionRequest)
        .filter(IngestionRequest.ingestion_id == test_uuid)
        .first()
    )
    assert fetched_row is not None
    assert fetched_row.source_type == "test_source"  # type: ignore[reportGeneralTypeIssues]
    assert fetched_row.status == "pending"  # type: ignore[reportGeneralTypeIssues]
    session.close()
