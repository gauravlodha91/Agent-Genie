from fastapi import APIRouter

from .services.retrieval_service import retrieve_chunks


router = APIRouter()


@router.post("/query")
async def query_document(query: str, top_k: int = 5):

    results, context = retrieve_chunks(query=query, top_k=top_k)

    return {"query": query, "results": results, "context": context}
