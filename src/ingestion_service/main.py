from fastapi import FastAPI

from ingestion_service.api.health import router as health_router

app = FastAPI(title="Agentic RAG Ingestion Service")

app.include_router(health_router)


@app.get("/")
def root():
    return {"service": "agentic-rag-ingestion"}
