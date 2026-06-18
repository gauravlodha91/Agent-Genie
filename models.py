from pydantic import BaseModel
from typing import Dict, List, Any


class Chunk(BaseModel):
    chunk_id: int
    content: str
    metadata: Dict[str, Any]


class ChunkMetadata(BaseModel):
    filename: str
    file_hash: str
    total_chunks: int
    chunks: List[Chunk]


class VectorStoreRequest(BaseModel):
    chunk_metadata: ChunkMetadata


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 5
