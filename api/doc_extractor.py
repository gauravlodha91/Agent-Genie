from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Any, Dict, List
from pathlib import Path
import hashlib
import json

from loggers import logger

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

router = APIRouter()

# Configuration
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}
DATA_FOLDER = "data"
CHUNKS_FOLDER = "./data/chunks"
GLOBAL_HASH_KEY = "agent-genie"

# Chunking configuration
DEFAULT_CHUNK_SIZE = 2048
DEFAULT_CHUNK_OVERLAP = 64


def ensure_folders():
    """Create necessary folders if they don't exist"""
    try:
        Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(CHUNKS_FOLDER).mkdir(parents=True, exist_ok=True)
        logger.info("Data folders created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating folders: {str(e)}")
        raise


def get_file_hash(filename: str) -> str:
    """Generate hash for filename"""
    hash_input = f"{GLOBAL_HASH_KEY}_{filename}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def save_uploaded_file(file: UploadFile, file_extension: str) -> str:
    """Save uploaded file to data folder"""
    try:
        file_hash = get_file_hash(file.filename)
        filename = f"{file_hash}{file_extension}"
        file_path = Path(DATA_FOLDER) / filename

        # Read and save file
        content = file.file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"File saved successfully: {filename}")
        return str(file_path)

    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise


def parse_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Parse PDF file using PyPDFLoader"""
    try:
        logger.info(f"Parsing PDF file: {file_path}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        parsed_docs = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "page": doc.metadata.get("page", 0),
            }
            for doc in documents
        ]

        logger.info(f"PDF parsed successfully. Pages: {len(parsed_docs)}")
        return parsed_docs

    except Exception as e:
        logger.error(f"Error parsing PDF: {str(e)}")
        raise


def parse_text(file_path: str) -> List[Dict[str, Any]]:
    """Parse TXT file"""

    # NEW: Tries multiple encodings in order

    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

    for encoding in encodings:
        try:
            loader = TextLoader(file_path, encoding=encoding)
            documents = loader.load()
            # Success! Break and use this encoding
            break
        except UnicodeDecodeError:
            # Try next encoding
            continue

    parsed_docs = [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in documents
    ]

    logger.info("TXT file parsed successfully")
    return parsed_docs


def parse_markdown(file_path: str) -> List[Dict[str, Any]]:
    """Parse Markdown file"""
    try:
        logger.info(f"Parsing Markdown file: {file_path}")
        loader = TextLoader(file_path)
        documents = loader.load()

        parsed_docs = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in documents
        ]

        logger.info("Markdown file parsed successfully")
        return parsed_docs

    except Exception as e:
        logger.error(f"Error parsing Markdown: {str(e)}")
        raise


def parse_docx(file_path: str) -> List[Dict[str, Any]]:
    """Parse DOCX file using UnstructuredWordDocumentLoader"""
    try:
        logger.info(f"Parsing DOCX file: {file_path}")
        loader = UnstructuredWordDocumentLoader(file_path)
        documents = loader.load()

        parsed_docs = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in documents
        ]

        logger.info("DOCX file parsed successfully")
        return parsed_docs

    except Exception as e:
        logger.error(f"Error parsing DOCX: {str(e)}")
        raise


def parse_through_extension(
    file_path: str, file_extension: str
) -> List[Dict[str, Any]]:
    """Route file parsing based on extension"""
    try:
        logger.info(f"Routing parser for extension: {file_extension}")

        extension_map = {
            ".pdf": parse_pdf,
            ".txt": parse_text,
            ".md": parse_markdown,
            ".docx": parse_docx,
        }

        parser = extension_map.get(file_extension.lower())
        if not parser:
            raise ValueError(f"No parser available for extension: {file_extension}")

        return parser(file_path)

    except Exception as e:
        logger.error(f"Error routing parser: {str(e)}")
        raise


def create_chunks_from_content(
    documents: List[Dict[str, Any]], chunk_size: int, chunk_overlap: int
) -> List[Dict[str, Any]]:
    """Create chunks from parsed documents using RecursiveCharacterTextSplitter"""
    try:
        logger.info(f"Creating chunks with size={chunk_size}, overlap={chunk_overlap}")

        # Initialize splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

        chunks = []
        chunk_id = 0

        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})

            # Split content into chunks
            split_texts = text_splitter.split_text(content)

            for split_text in split_texts:
                chunk = {
                    "chunk_id": chunk_id,
                    "content": split_text,
                    "metadata": metadata,
                    "chunk_size": len(split_text),
                }
                chunks.append(chunk)
                chunk_id += 1

        logger.info(f"Chunks created successfully. Total chunks: {len(chunks)}")
        return chunks

    except Exception as e:
        logger.error(f"Error creating chunks: {str(e)}")
        raise


def save_chunks_metadata(
    filename: str, chunks: List[Dict[str, Any]], original_filename: str
) -> Dict[str, Any]:
    """Save chunks metadata to JSON file"""
    try:
        file_hash = get_file_hash(original_filename)
        metadata_file = Path(CHUNKS_FOLDER) / f"{file_hash}_metadata.json"

        metadata = {
            "filename": original_filename,
            "file_hash": file_hash,
            "total_chunks": len(chunks),
            "saved_at": datetime.now().isoformat(),
            "chunks": chunks,
        }

        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Chunks metadata saved: {metadata_file}")
        return metadata

    except Exception as e:
        logger.error(f"Error saving chunks metadata: {str(e)}")
        raise


async def process_uploaded_file(
    file: UploadFile,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> Dict[str, Any]:
    """Main function to process uploaded file"""

    try:
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in ALLOWED_EXTENSIONS:
            logger.warning(f"Unsupported file type: {file_extension}")
            raise ValueError(
                f"Unsupported file type: {file_extension}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        logger.info(f"Processing file: {file.filename} (size: {file.size} bytes)")

        # Ensure folders exist
        ensure_folders()

        # Save uploaded file
        file_path = save_uploaded_file(file, file_extension)

        # Parse file based on extension
        parsed_documents = parse_through_extension(file_path, file_extension)

        if not parsed_documents:
            raise ValueError("No content extracted from file")

        # Create chunks
        chunks = create_chunks_from_content(parsed_documents, chunk_size, chunk_overlap)

        # Save chunks metadata
        chunks_metadata = save_chunks_metadata(file_path, chunks, file.filename)

        # Prepare response
        response = {
            "status": "success",
            "filename": file.filename,
            "file_extension": file_extension,
            "file_hash": get_file_hash(file.filename),
            "total_documents": len(parsed_documents),
            "total_chunks": len(chunks),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "processed_at": datetime.now().isoformat(),
            "file_path": file_path,
            "chunk_metadata": chunks_metadata,
        }

        logger.info(f"File processing completed successfully: {file.filename}")
        return response

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_uploaded_file: {str(e)}")
        raise


@router.post("/upload_doc")
async def upload_doc(
    file: UploadFile = File(...),
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
):
    """
    Upload and process document

    Parameters:
    - file: Document file (.pdf, .txt, .md, .docx)
    - chunk_size: Size of text chunks (default: 2048)
    - chunk_overlap: Overlap between chunks (default: 64)
    """
    try:
        logger.info(
            f"Upload request received - File: {file.filename}, chunk_size={chunk_size}, overlap={chunk_overlap}"
        )

        result = await process_uploaded_file(
            file=file, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        return JSONResponse(status_code=200, content=result)

    except ValueError as e:
        logger.warning(f"Invalid input: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)},
        )

    except Exception as e:
        logger.error(f"Internal server error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Internal Server Error: {str(e)}",
            },
        )
