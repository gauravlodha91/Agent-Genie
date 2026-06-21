from typing import Any

from chromadb.api.types import Metadata
from fastapi import APIRouter

from models import VectorStoreRequest

from .services.chroma_service import store_chunks
from .services.embedding_service import embed_documents

router = APIRouter()

metadatas: list[Metadata] = []


@router.post("/store_chunks")
async def store_chunks_route(payload: VectorStoreRequest) -> dict[str, Any]:
    """
    Store parsed chunks in ChromaDB.
    """

    chunks = payload.chunk_metadata.chunks

    documents = []
    metadatas: list[Metadata] = []

    ids = []

    for chunk in chunks:
        documents.append(chunk.content)

        ids.append(f"{payload.chunk_metadata.file_hash}_{chunk.chunk_id}")
        metadata: Metadata = {
            "file_hash": payload.chunk_metadata.file_hash,
            "filename": payload.chunk_metadata.filename,
            "chunk_id": chunk.chunk_id,
            **chunk.metadata,
        }

        metadatas.append(metadata)

        # metadatas.append(
        #     {
        #         "file_hash": payload.chunk_metadata.file_hash,
        #         "filename": payload.chunk_metadata.filename,
        #         "chunk_id": chunk.chunk_id,
        #         **chunk.metadata,
        #     }
        # )

    embeddings = embed_documents(documents)

    result = store_chunks(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

    return {
        "status": "success",
        "chunks_stored": len(chunks),
        "collection_stats": result,
    }
