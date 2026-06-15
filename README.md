# Document Upload & Processing API

## Overview

A FastAPI-based document processing system that handles multiple file formats (PDF, TXT, Markdown, DOCX), parses them, and creates semantically meaningful chunks using LangChain.

## Features

✅ Multi-format support (.pdf, .txt, .md, .docx)
✅ LangChain document loaders for robust parsing
✅ Recursive character text splitting with customizable chunk size
✅ Comprehensive logging (console + file rotation)
✅ Structured JSON responses
✅ File hashing for unique identification
✅ Metadata persistence
✅ Error handling with detailed logging

## Project Structure

```
project/
├── loggers.py              # Logger configuration
├── upload_handler.py       # Main upload and parsing logic
├── main.py                # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── data/                   # Uploaded files storage
├── data/chunks/            # Chunk metadata storage
└── logs/                   # Application logs
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Application

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### Upload Document

**POST** `/api/upload_doc`

#### Parameters

- `file` (UploadFile, required): Document file (.pdf, .txt, .md, .docx)
- `chunk_size` (int, optional): Size of text chunks (default: 2048)
- `chunk_overlap` (int, optional): Overlap between chunks (default: 64)

#### cURL Example

```bash
curl -X POST "http://localhost:8000/api/upload_doc" \
  -F "file=@document.pdf" \
  -F "chunk_size=2048" \
  -F "chunk_overlap=64"
```

#### Python Example

```python
import requests

with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "chunk_size": 2048,
        "chunk_overlap": 64
    }
    response = requests.post(
        "http://localhost:8000/api/upload_doc",
        files=files,
        data=data
    )
    print(response.json())
```

#### Response (Success - 200)

```json
{
  "status": "success",
  "filename": "document.pdf",
  "file_extension": ".pdf",
  "file_hash": "a1b2c3d4e5f6g7h8",
  "total_documents": 5,
  "total_chunks": 48,
  "chunk_size": 2048,
  "chunk_overlap": 64,
  "processed_at": "2024-01-15T10:30:45.123456",
  "file_path": "data/a1b2c3d4e5f6g7h8.pdf"
}
```

#### Response (Error - 400)

```json
{
  "status": "error",
  "message": "Unsupported file type: .xlsx. Allowed: .pdf, .txt, .md, .docx"
}
```

#### Response (Error - 500)

```json
{
  "status": "error",
  "message": "Internal Server Error: [specific error details]"
}
```

## Health Check

**GET** `/`

```json
{
  "status": "healthy",
  "message": "Document Processing API is running"
}
```

## File Storage Structure

### Data Folder (`/data`)

```
data/
├── a1b2c3d4e5f6g7h8.pdf
├── b2c3d4e5f6g7h8i9.txt
└── chunks/
    ├── a1b2c3d4e5f6g7h8_metadata.json
    └── b2c3d4e5f6g7h8i9_metadata.json
```

### Chunks Metadata Format

```json
{
  "filename": "document.pdf",
  "file_hash": "a1b2c3d4e5f6g7h8",
  "total_chunks": 48,
  "saved_at": "2024-01-15T10:30:45.123456",
  "chunks": [
    {
      "chunk_id": 0,
      "content": "This is the first chunk of text...",
      "metadata": {
        "source": "data/a1b2c3d4e5f6g7h8.pdf",
        "page": 0
      },
      "chunk_size": 1950
    },
    {
      "chunk_id": 1,
      "content": "This is the second chunk...",
      "metadata": {},
      "chunk_size": 2048
    }
  ]
}
```

## Logging

### Log Levels

- **INFO**: File uploads, parsing, chunking operations
- **WARNING**: Validation errors, unsupported formats
- **ERROR**: Processing failures, internal errors

### Log Output

Logs are written to:

1. **Console**: Real-time log output
2. **File**: `logs/app.log` (rotated every 10MB, keeps 5 backups)

### Sample Log Output

```
2024-01-15 10:30:45,123 - app - INFO - Upload request received - File: document.pdf, chunk_size=2048, overlap=64
2024-01-15 10:30:45,145 - app - INFO - Processing file: document.pdf (size: 524288 bytes)
2024-01-15 10:30:45,150 - app - INFO - Data folders created/verified successfully
2024-01-15 10:30:45,155 - app - INFO - File saved successfully: a1b2c3d4e5f6g7h8.pdf
2024-01-15 10:30:45,200 - app - INFO - Parsing PDF file: data/a1b2c3d4e5f6g7h8.pdf
2024-01-15 10:30:45,500 - app - INFO - PDF parsed successfully. Pages: 5
2024-01-15 10:30:45,520 - app - INFO - Creating chunks with size=2048, overlap=64
2024-01-15 10:30:45,650 - app - INFO - Chunks created successfully. Total chunks: 48
2024-01-15 10:30:45,670 - app - INFO - Chunks metadata saved: data/chunks/a1b2c3d4e5f6g7h8_metadata.json
2024-01-15 10:30:45,675 - app - INFO - File processing completed successfully: document.pdf
```

## Chunking Strategy

### RecursiveCharacterTextSplitter

The implementation uses LangChain's `RecursiveCharacterTextSplitter` with the following separator hierarchy:

1. **Double newline** (`\n\n`): Paragraph breaks
2. **Single newline** (`\n`): Line breaks
3. **Space** (` `): Word boundaries
4. **Empty string** (`""`): Character level (last resort)

This ensures that chunks respect natural semantic boundaries while maintaining the specified chunk size.

### Parameters

- `chunk_size`: Maximum characters per chunk (default: 2048)
- `chunk_overlap`: Character overlap between consecutive chunks (default: 64)

## Supported File Formats

| Format        | Extension | Loader                         | Status       |
| ------------- | --------- | ------------------------------ | ------------ |
| PDF           | .pdf      | PyPDFLoader                    | ✅ Supported |
| Plain Text    | .txt      | TextLoader                     | ✅ Supported |
| Markdown      | .md       | TextLoader                     | ✅ Supported |
| Word Document | .docx     | UnstructuredWordDocumentLoader | ✅ Supported |

## Error Handling

### Common Errors & Solutions

#### 1. Unsupported File Type

```
Error: Unsupported file type: .xlsx. Allowed: .pdf, .txt, .md, .docx
```

**Solution**: Only upload supported file formats.

#### 2. File Not Found

```
Error: [Errno 2] No such file or directory: 'data/...'
```

**Solution**: Ensure the `data` folder is created. The application creates it automatically on first run.

#### 3. PDF Parsing Error

```
Error parsing PDF: PdfReadError
```

**Solution**: Verify the PDF is not corrupted and is not password-protected.

#### 4. Memory Error with Large Files

```
Error: MemoryError
```

**Solution**: Reduce `chunk_size` or process files in smaller batches.

## Performance Optimization Tips

1. **Adjust Chunk Size**: Smaller chunks = more requests but faster processing

   ```python
   chunk_size=1024  # Faster, more granular
   chunk_size=4096  # Slower, broader context
   ```

2. **Optimize Overlap**: Balance context vs. redundancy

   ```python
   chunk_overlap=32   # Less overlap, smaller output
   chunk_overlap=128  # More context, larger output
   ```

3. **Batch Processing**: Process multiple files asynchronously
   ```python
   async with asyncio.TaskGroup() as tg:
       for file in files:
           tg.create_task(process_uploaded_file(file))
   ```

## Extending the Code

### Adding New File Format Support

1. Create a parser function:

```python
def parse_excel(file_path: str) -> List[Dict[str, Any]]:
    try:
        logger.info(f"Parsing Excel file: {file_path}")
        loader = UnstructuredExcelLoader(file_path)
        documents = loader.load()
        # ... process documents
        return parsed_docs
    except Exception as e:
        logger.error(f"Error parsing Excel: {str(e)}")
        raise
```

2. Add extension to `ALLOWED_EXTENSIONS`:

```python
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".xlsx"}
```

3. Add to parser routing:

```python
extension_map = {
    # ... existing entries
    ".xlsx": parse_excel,
}
```

## Best Practices

✅ Always validate file uploads before processing
✅ Use meaningful chunk sizes based on your use case (RAG, search, etc.)
✅ Monitor logs for errors and patterns
✅ Implement rate limiting for production
✅ Store chunks metadata for retrieval
✅ Use file hashing for deduplication
✅ Regularly rotate and archive logs

## Testing

### Manual Testing with cURL

```bash
# Upload a PDF
curl -X POST http://localhost:8000/api/upload_doc \
  -F "file=@sample.pdf" \
  -F "chunk_size=2048" \
  -F "chunk_overlap=64"

# Check health
curl http://localhost:8000/
```

### Python Unit Test Template

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_pdf():
    with open("test_files/sample.pdf", "rb") as f:
        response = client.post(
            "/api/upload_doc",
            files={"file": f},
            data={"chunk_size": 2048, "chunk_overlap": 64}
        )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_unsupported_format():
    with open("test_files/sample.xlsx", "rb") as f:
        response = client.post("/api/upload_doc", files={"file": f})
    assert response.status_code == 400
    assert "Unsupported" in response.json()["message"]
```

## Dependencies Version Info

- FastAPI: 0.104.1
- LangChain: 0.1.0
- PyPDF: 3.17.1
- python-docx: 0.8.11
- Unstructured: 0.11.2

## License

MIT

## Support

For issues or questions, check the logs first (`logs/app.log`) for detailed error messages.
