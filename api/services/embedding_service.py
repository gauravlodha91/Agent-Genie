from collections.abc import Sequence
from typing import cast

import cohere

from utils.config import COHERE_CONFIG

COHERE_API_KEY = COHERE_CONFIG["api_key"]
COHERE_MODEL = COHERE_CONFIG["model"]


co = cohere.Client(COHERE_API_KEY)


def embed_documents(texts: list[str]) -> list[Sequence[float]]:
    response = co.embed(texts=texts, model=COHERE_MODEL, input_type="search_document")

    embeddings = cast(list[Sequence[float]], response.embeddings)

    return embeddings


def embed_query(query: str) -> Sequence[float]:
    response = co.embed(texts=[query], model=COHERE_MODEL, input_type="search_query")

    if not isinstance(response.embeddings, list):
        raise ValueError("Unexpected embedding response")

    return response.embeddings[0]
