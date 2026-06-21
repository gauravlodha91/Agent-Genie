# RAG Starter Template

## Overview

This branch serves as a **starter template for building Retrieval-Augmented Generation (RAG) applications**. It is intentionally designed to be simple and easy to understand, making it ideal for developers who are new to Generative AI and RAG-based systems.

**This is not a production-ready implementation or a final architecture.** Instead, think of it as a foundation that demonstrates the core building blocks required to create a RAG application.

The goal of this template is to help you understand:

- How documents are uploaded and processed
- How chunking works and why it is important
- How embeddings are generated and stored
- How vector databases are integrated
- How retrieval is performed during querying
- Basic project structuring and code organization
- Logging best practices for debugging and monitoring

To make learning easier, the project includes dedicated folders for document storage, chunk inspection, and logging so that you can clearly see what happens at each stage of the RAG pipeline.

This implementation focuses only on a **basic text-based RAG workflow**. Advanced concepts such as Hybrid Search, Re-ranking, Graph RAG, Agentic RAG, Multi-Agent Systems, Memory, Guardrails, and Multimodal Processing have intentionally been excluded to keep the learning curve simple.

You are encouraged to use this branch as a starting point and customize it based on your own requirements and experiments.

---

## Configure `pyproject.toml`

1. Rename `sample_pyproject.toml` to `pyproject.toml`.

2. Update the configuration values below:

   ```toml
   [app.cohere]
   model = "embed-v4.0"
   api_key = "YOUR_COHERE_API_KEY"

   [app.chromadb]
   collection_name = "document_chunks"
   persist_directory = "./chroma_db"

   [app.groq]
   model = "llama-3.3-70b-versatile"
   api_key = "YOUR_GROQ_API_KEY"
   ```

---

## Project Structure

    ```
    Agent-Genie/
    │
    ├── api/
    │   ├── __init__.py
    │   ├── chunk_index.py
    │   ├── chunk_retrieve.py
    |   ├── doc_extractor.py
    |   ├── heartbeat_api.py
    │   └── services/
    │       ├── __init__.py
    │       ├── chroma_service.py
    │       ├── embedding_service.py
    │       └── retrieval_service.py
    │
    ├── data/chunks
    |
    ├── document_chunks (vector_database)
    |
    ├── logs/
    |
    ├── utils/
    │   ├── __init__.py
    │   └── config.py
    │
    ├── test/
    │   ├── __init__.py
    │   └── test_one.py
    │
    ├── loggers.py
    ├── main.py
    ├── models.py
    ├── pyproject.toml
    └── README.md
    ```

---

## Installation

### 1. Install Poetry

```bash
pip install poetry
```

### 2. Install Project Dependencies

```bash
poetry install
```

To update dependencies:

```bash
poetry update
```

---

## Run the Application

Start the FastAPI server:

```bash
poetry run python main.py
```

Once the application starts, open the generated URL and append:

```text
/docs
```

Example:

```text
http://127.0.0.1:8000/docs
```

This will open the FastAPI Swagger UI.

---

## Available APIs

### 1. `/heartbeat`

Health check endpoint to verify that the application is running.

### 2. `/upload_doc`

Upload a document for processing and storage.

### 3. `/store_chunk`

Generate embeddings and store document chunks in ChromaDB.

### 4. `/query`

Perform retrieval against stored chunks and generate an answer using the configured LLM.

---

## Basic RAG Flow

1. Upload a document using `/upload_doc`
2. Chunk the document and store embeddings using `/store_chunk`
3. Ask questions using `/query`
4. Retrieved chunks are passed to the LLM as context
5. The LLM generates a response grounded in the retrieved information

This workflow demonstrates the fundamental principles of Retrieval-Augmented Generation (RAG) and provides a clean starting point for building more advanced GenAI applications.
