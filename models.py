from typing import Any

from pydantic import BaseModel


class Chunk(BaseModel):
    chunk_id: int
    content: str
    metadata: dict[str, Any]


class ChunkMetadata(BaseModel):
    filename: str
    file_hash: str
    total_chunks: int
    chunks: list[Chunk]


class VectorStoreRequest(BaseModel):
    chunk_metadata: ChunkMetadata


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 5
