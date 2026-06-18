import chromadb
from utils.config import CHROMA_CONFIG
from loggers import logger
from .embedding_service import embed_documents

COLLECTION_NAME = CHROMA_CONFIG["collection_name"]
PERSISTED_DIRECTORY = CHROMA_CONFIG["collection_name"]

client = chromadb.PersistentClient(path=PERSISTED_DIRECTORY)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


# def store_chunks(ids, documents, embeddings, metadatas):
#     try:
#         collection.add(
#             ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
#         )

#         return {"collection_name": collection.name, "count": collection.count()}

#     except Exception as e:
#         logger.error(f"Error at store_chunk method as {e}")


# def recur(n: int):
#     return 1 if n == 1 else (n + recur(n - 1))


def store_chunks(chunks):

    docs = []
    ids = []
    metadatas = []

    try:
        for chunk in chunks:
            docs.append(chunk["content"])

            ids.append(f"{chunk['file_hash']}_{chunk['chunk_id']}")

            metadatas.append(chunk["metadata"])

        embeddings = embed_documents(docs)

        collection.add(
            ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas
        )

        return {"collection_name": collection.name, "count": collection.count()}

    except Exception as e:
        logger.error(f"Error at store_chunk method as {e}")
