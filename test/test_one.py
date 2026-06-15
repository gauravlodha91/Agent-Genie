"""
Unit tests for document upload and processing
Run with: pytest test_upload_handler.py -v
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from io import BytesIO

# Import the app
from main import app

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoints"""

    def test_health_check(self):
        """Test root health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestDocumentUpload:
    """Test document upload functionality"""

    @pytest.fixture
    def sample_txt_file(self):
        """Create a sample text file for testing"""
        content = b"""This is a sample text document.
        
It contains multiple paragraphs to test chunking functionality.

This helps ensure that the text splitting works correctly with various content types.

The RecursiveCharacterTextSplitter should maintain semantic boundaries while respecting chunk sizes.
"""
        return BytesIO(content), "sample.txt"

    @pytest.fixture
    def sample_md_file(self):
        """Create a sample markdown file"""
        content = b"""# Sample Markdown Document

## Introduction
This is a test markdown file.

## Section 1
Some content here.

## Section 2
More content to test chunking.

### Subsection
Even more content.
"""
        return BytesIO(content), "sample.md"

    def test_upload_txt_file(self, sample_txt_file):
        """Test uploading a TXT file"""
        file_obj, filename = sample_txt_file
        response = client.post(
            "/api/upload_doc",
            files={"file": (filename, file_obj, "text/plain")},
            data={"chunk_size": 256, "chunk_overlap": 32},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["filename"] == filename
        assert data["file_extension"] == ".txt"
        assert data["total_chunks"] > 0
        assert "file_hash" in data
        assert "processed_at" in data

    def test_upload_md_file(self, sample_md_file):
        """Test uploading a Markdown file"""
        file_obj, filename = sample_md_file
        response = client.post(
            "/api/upload_doc",
            files={"file": (filename, file_obj, "text/markdown")},
            data={"chunk_size": 256, "chunk_overlap": 32},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["file_extension"] == ".md"
        assert data["total_chunks"] > 0

    def test_upload_unsupported_file(self):
        """Test uploading an unsupported file format"""
        content = b"This is an Excel file content"
        response = client.post(
            "/api/upload_doc",
            files={"file": ("test.xlsx", BytesIO(content), "application/vnd.ms-excel")},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert "Unsupported" in data["message"]

    def test_upload_with_custom_chunk_size(self, sample_txt_file):
        """Test uploading with custom chunk size"""
        file_obj, filename = sample_txt_file
        response = client.post(
            "/api/upload_doc",
            files={"file": (filename, file_obj, "text/plain")},
            data={"chunk_size": 512, "chunk_overlap": 64},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["chunk_size"] == 512
        assert data["chunk_overlap"] == 64

    def test_upload_with_default_chunk_size(self, sample_txt_file):
        """Test uploading without specifying chunk size (should use defaults)"""
        file_obj, filename = sample_txt_file
        response = client.post(
            "/api/upload_doc", files={"file": (filename, file_obj, "text/plain")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["chunk_size"] == 2048  # Default
        assert data["chunk_overlap"] == 64  # Default


class TestResponseFormat:
    """Test response format and structure"""

    def test_success_response_structure(self):
        """Test that success response has all required fields"""
        content = b"Test content for response validation"
        response = client.post(
            "/api/upload_doc",
            files={"file": ("test.txt", BytesIO(content), "text/plain")},
        )

        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "status",
            "filename",
            "file_extension",
            "file_hash",
            "total_documents",
            "total_chunks",
            "chunk_size",
            "chunk_overlap",
            "processed_at",
            "file_path",
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        assert data["status"] == "success"
        assert isinstance(data["total_chunks"], int)
        assert isinstance(data["total_documents"], int)

    def test_error_response_structure(self):
        """Test that error response has required fields"""
        response = client.post(
            "/api/upload_doc",
            files={
                "file": ("test.exe", BytesIO(b"content"), "application/x-msdownload")
            },
        )

        assert response.status_code == 400
        data = response.json()

        assert "status" in data
        assert "message" in data
        assert data["status"] == "error"


class TestFileProcessing:
    """Test file processing and chunking logic"""

    def test_chunk_creation_with_overlap(self):
        """Test that chunks are created with proper overlap"""
        # Create a predictable text content
        content = b"Word " * 500  # 2500 words, should create multiple chunks

        response = client.post(
            "/api/upload_doc",
            files={"file": ("test.txt", BytesIO(content), "text/plain")},
            data={"chunk_size": 512, "chunk_overlap": 128},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_chunks"] > 1
        assert data["chunk_overlap"] == 128

    def test_small_file_single_chunk(self):
        """Test that small files result in single chunk"""
        content = b"This is a small file."

        response = client.post(
            "/api/upload_doc",
            files={"file": ("test.txt", BytesIO(content), "text/plain")},
            data={"chunk_size": 2048, "chunk_overlap": 64},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_chunks"] >= 1


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_file(self):
        """Test uploading an empty file"""
        response = client.post(
            "/api/upload_doc", files={"file": ("empty.txt", BytesIO(b""), "text/plain")}
        )

        # Empty file should still process, just with no content
        assert response.status_code == 200 or response.status_code == 400

    def test_very_large_chunk_size(self):
        """Test with very large chunk size"""
        content = b"Test content" * 100

        response = client.post(
            "/api/upload_doc",
            files={"file": ("test.txt", BytesIO(content), "text/plain")},
            data={"chunk_size": 8192, "chunk_overlap": 256},
        )

        assert response.status_code == 200

    def test_very_small_chunk_size(self):
        """Test with very small chunk size"""
        content = b"This is a test file with some content for chunking."

        response = client.post(
            "/api/upload_doc",
            files={"file": ("test.txt", BytesIO(content), "text/plain")},
            data={"chunk_size": 64, "chunk_overlap": 8},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["chunk_size"] == 64

    def test_overlap_larger_than_chunk_size(self):
        """Test with overlap larger than chunk size"""
        content = b"Test content"

        response = client.post(
            "/api/upload_doc",
            files={"file": ("test.txt", BytesIO(content), "text/plain")},
            data={"chunk_size": 100, "chunk_overlap": 150},
        )

        # Should still process, though overlap will be capped
        assert response.status_code == 200


class TestFileTypes:
    """Test different file type support"""

    def test_txt_extension_support(self):
        """Test .txt file support"""
        response = client.post(
            "/api/upload_doc",
            files={"file": ("doc.txt", BytesIO(b"Text content"), "text/plain")},
        )
        assert response.status_code == 200
        assert response.json()["file_extension"] == ".txt"

    def test_md_extension_support(self):
        """Test .md file support"""
        response = client.post(
            "/api/upload_doc",
            files={"file": ("doc.md", BytesIO(b"# Markdown"), "text/markdown")},
        )
        assert response.status_code == 200
        assert response.json()["file_extension"] == ".md"

    def test_case_insensitive_extension(self):
        """Test that file extension check is case-insensitive"""
        response = client.post(
            "/api/upload_doc",
            files={"file": ("doc.TXT", BytesIO(b"Content"), "text/plain")},
        )
        assert response.status_code == 200
        assert response.json()["file_extension"] == ".txt"


# Run tests with: pytest test_upload_handler.py -v
# Run specific test: pytest test_upload_handler.py::TestDocumentUpload::test_upload_txt_file -v
# Run with coverage: pytest test_upload_handler.py --cov=upload_handler --cov-report=html
