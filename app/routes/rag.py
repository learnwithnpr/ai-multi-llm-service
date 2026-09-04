"""
rag.py  (app/routes/rag.py)
---------------------------
Route: POST /api/upload-document

This endpoint lets students upload a plain-text (.txt) file directly from
Swagger UI at http://localhost:8000/docs.

Flow:
  1. FastAPI receives the file via UploadFile.
  2. document_service reads the raw text.
  3. document_service splits the text into chunks.
  4. chroma_service stores the chunks in ChromaDB.
  5. We return a JSON response confirming how many chunks were saved.
"""

from fastapi import APIRouter, HTTPException, UploadFile

from app.core.logger import get_logger
from app.services import chroma_service, document_service

router = APIRouter()
logger = get_logger()


@router.post("/upload-document")
def upload_document(uploaded_file: UploadFile):
    """Upload a document and store its contents in ChromaDB for RAG retrieval.

    Supported file types:
      .txt, .md, .csv, .log  — Plain text
      .docx                  — Word documents
      .pdf                   — PDF documents
      .pptx                  — PowerPoint presentations
      .html, .htm            — HTML files
      .json                  — JSON files

    How to test in Swagger UI (/docs):
      1. Click on POST /api/upload-document.
      2. Click "Try it out".
      3. Click "Choose File" and pick a file from your computer.
      4. Click "Execute".
      5. You should see { "message": "...", "total_chunks": N } in the response.
    """
    logger.info("UPLOAD   file=%s", uploaded_file.filename)

    try:
        # ── Step 1: Read the file into a plain Python string ─────────────────
        raw_text = document_service.read_text_from_uploaded_file(uploaded_file)

        if not raw_text.strip():
            # The file was empty or contained only whitespace — nothing to store.
            raise ValueError("The uploaded file appears to be empty.")

        # ── Step 2: Split the text into small, overlapping chunks ─────────────
        text_chunks = document_service.split_text_into_chunks(raw_text)

        logger.info(
            "CHUNKED  file=%s  chunks=%d",
            uploaded_file.filename,
            len(text_chunks),
        )

        # ── Step 3: Store each chunk in ChromaDB ──────────────────────────────
        total_chunks_stored = chroma_service.add_documents_to_collection(
            text_chunks=text_chunks,
            document_name=uploaded_file.filename,
        )

    except ValueError as error:
        # Friendly errors (empty file, bad format) → 400 Bad Request
        logger.warning("UPLOAD FAILED  file=%s  reason=%s", uploaded_file.filename, error)
        raise HTTPException(status_code=400, detail=str(error)) from error

    except Exception as error:
        # Unexpected errors (ChromaDB unreachable, etc.) → 500
        logger.exception("UPLOAD ERROR  file=%s  %s", uploaded_file.filename, error)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {error}",
        ) from error

    # ── Step 4: Return a confirmation to the caller ───────────────────────────
    return {
        "message": f"'{uploaded_file.filename}' uploaded and stored successfully.",
        "total_chunks": total_chunks_stored,
    }
