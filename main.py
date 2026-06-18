from fastapi import FastAPI
import uvicorn

from loggers import logger
from api.heartbeat_api import router as heartbeat_router
from api.doc_extractor import router as upload_doc_router
from api.chunk_index import router as chunk_indexer_router
from api.chunk_retrieve import router as retriever_router

app = FastAPI()


app.include_router(heartbeat_router, tags=["health"])
app.include_router(upload_doc_router)
app.include_router(chunk_indexer_router)
app.include_router(retriever_router)


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("Application startup")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("Application shutdown")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
