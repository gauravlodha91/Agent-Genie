import cohere
from typing import List

from utils.config import COHERE_CONFIG


COHERE_API_KEY = COHERE_CONFIG["api_key"]
COHERE_MODEL = COHERE_CONFIG["model"]


co = cohere.Client(COHERE_API_KEY)


def embed_documents(texts: list[str]) -> list[list[float]]:
    response = co.embed(texts=texts, model=COHERE_MODEL, input_type="search_document")

    return response.embeddings


def embed_query(query: str) -> list[float]:
    response = co.embed(texts=[query], model=COHERE_MODEL, input_type="search_query")

    return response.embeddings[0]
