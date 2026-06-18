from .embedding_service import embed_query
from .chroma_service import collection
from loggers import logger
from langchain_groq import ChatGroq
from utils.config import GROQ_CONFIG


GROQ_API_KEY = GROQ_CONFIG["api_key"]
GROQ_MODEL_NAME = GROQ_CONFIG["model"]


def retrieve_chunks(query: str, top_k: int = 5):

    try:
        query_embedding = embed_query(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        documents = results["documents"][0]
        context = "\n\n".join(documents)

        logger.info(f"Retrieve context :: {context}")

        return summarize_context(query=query, context=context), context

    except Exception as e:
        logger.error(f"Error at store_chunk method as {e}")


def summarize_context(query: str, context: str):

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
        model_name=GROQ_MODEL_NAME,
        api_key=GROQ_API_KEY,
        temperature=0.7,
        max_tokens=700,
    )
    # Invoke model
    response = llm.invoke(prompt)
    print(response.content)

    return response.content
