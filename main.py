from fastapi import FastAPI
from app.api.routes import router
from app.api.rag_router import router as rag_router

app = FastAPI(title="ETL Document Service")

app.include_router(router)
app.include_router(rag_router)

@app.get("/health")
def health():
    return {"status": "ok"}