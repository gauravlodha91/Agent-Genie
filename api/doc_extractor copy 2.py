from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from datetime import datetime

# from models import UploadDoc
from typing import Any, Dict, List
from pathlib import Path

from loggers import logger

router = APIRouter()


ALLOWED_EXTENSIONS = [".md", ".txt"]
DATA_FOLDER = "data"
GLOBAL_HASH_KEY = "agent-genie"


def ensure_data_folder():
    Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)


def save_to_markdown(content, filename): ...
def parse_pdf(file_path): ...
def parse_text(file_path): ...
def parse_markdown(file_path): ...
def parse_excel(file_path): ...
def parse_docx(file_path): ...


def parse_through_extension(file_path_extension): ...


def create_chunks_from_content(): ...


async def process_uploaded_file(
    file, chunk_size: int = 2048, chunk_overlap: int = 64
) -> Dict[str, Any]:

    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported File Type : {file_extension}")

    return {"status": "okay", "filename": file_extension}


@router.post("/upload_doc")
async def upload_doc(
    file: UploadFile = File(...),
    chunk_size: int = 2048,
    chunk_overlap: int = 64,
):
    try:
        logger.info(f"File ready with chunk_size={chunk_size}, overlap={chunk_overlap}")
        result = await process_uploaded_file(
            file=file, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        return JSONResponse(status_code=200, content=result)

    except ValueError as e:
        return JSONResponse(
            status_code=400, content={"status": "Error", "message": str(e)}
        )

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": "Error",
                "message": f" Internal Server Error :: {str(e)}",
            },
        )
