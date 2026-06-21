from collections.abc import Sequence

import chromadb
from chromadb.api.types import Metadata

from loggers import logger
from utils.config import CHROMA_CONFIG

COLLECTION_NAME = CHROMA_CONFIG["collection_name"]
PERSISTED_DIRECTORY = CHROMA_CONFIG["collection_name"]

client = chromadb.PersistentClient(path=PERSISTED_DIRECTORY)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def store_chunks(
    ids: list[str],
    documents: list[str],
    embeddings: list[Sequence[float]],
    metadatas: list[Metadata],
) -> dict[str, str | int]:

    try:
        collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

        return {"collection_name": collection.name, "count": collection.count()}

    except Exception as e:
        logger.error(f"Error at store_chunk method as {e}")
        raise
