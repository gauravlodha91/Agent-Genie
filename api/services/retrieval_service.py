from collections.abc import Sequence

from langchain_groq import ChatGroq

from loggers import logger
from utils.config import GROQ_CONFIG

from .chroma_service import collection
from .embedding_service import embed_query

GROQ_API_KEY = GROQ_CONFIG["api_key"]
GROQ_MODEL_NAME = GROQ_CONFIG["model"]


def retrieve_chunks(query: str, top_k: int = 5) -> tuple[str, str]:
    try:
        # query_embedding = embed_query(query)
        query_embedding: Sequence[float] = embed_query(query)

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        documents = results.get("documents")

        if not documents:
            return ("No relevant documents found", "")

        context = "\n\n".join(documents[0])

        logger.info(f"Retrieve context :: {context}")

        return (
            summarize_context(query=query, context=context),
            context,
        )

    except Exception as e:
        logger.error(f"Error at store_chunk method as {e}")
        return ("", "")


def summarize_context(query: str, context: str) -> str:

    prompt = f"""
        Question:
        {query}

        Context:
        {context}

        Instructions:
        - Answer only from context
        - Be concise
        - Summarize key points
        - If information is unavailable, say so
        """

    # Initialize Groq model

    llm = ChatGroq(
        model=GROQ_MODEL_NAME,
        api_key=GROQ_API_KEY,
        temperature=0.7,
        max_tokens=700,
    )
    # Invoke model
    response = llm.invoke(prompt)
    print(response.content)
    return str(response.content)
    # return response.content
