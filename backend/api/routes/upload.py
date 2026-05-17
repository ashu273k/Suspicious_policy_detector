"""
Upload Route — Handle document upload, parsing, and storage.
"""

import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from config import UPLOAD_DIR
from ingestion.parser import parse_document
from ingestion.preprocessor import preprocess
from api.schemas import UploadResponse, UploadTextRequest

router = APIRouter()

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_PASTE_CHARS = 100_000

# In-memory document store (replace with DB in production)
documents = {}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a contract document (PDF, DOCX, or TXT).
    Parses the document and stores the extracted text.
    """
    # Validate file type
    allowed_types = {".pdf", ".docx", ".doc", ".txt"}
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    safe_name = Path(file.filename).name
    ext = Path(safe_name).suffix.lower()

    if ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed_types)}",
        )

    # Generate unique document ID
    doc_id = str(uuid.uuid4())[:12]

    # Save uploaded file
    file_path = UPLOAD_DIR / f"{doc_id}{ext}"
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file_path.stat().st_size > MAX_UPLOAD_BYTES:
            file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=413, detail="Uploaded file is too large")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Parse document
    try:
        parsed = parse_document(str(file_path))
    except Exception as e:
        # Clean up file on parse failure
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Failed to parse document: {e}")

    # Preprocess text
    cleaned_text = preprocess(parsed["text"])

    # Store document metadata and text
    documents[doc_id] = {
        "id": doc_id,
        "filename": safe_name,
        "file_path": str(file_path),
        "text": cleaned_text,
        "page_count": parsed["page_count"],
        "char_count": len(cleaned_text),
        "format": parsed["format"],
    }

    return UploadResponse(
        document_id=doc_id,
        filename=safe_name,
        page_count=parsed["page_count"],
        char_count=len(cleaned_text),
        status="uploaded",
    )


def get_document(doc_id: str) -> dict:
    """Retrieve a stored document by ID."""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")
    return documents[doc_id]


@router.post("/upload_text", response_model=UploadResponse)
async def upload_text(payload: UploadTextRequest):
    """
    Upload raw contract text (paste). Expects JSON: {"text": "...", "filename": "optional name"}
    """
    text = payload.text
    filename = Path(payload.filename).name or "pasted_contract.txt"

    if len(text) > MAX_PASTE_CHARS:
        raise HTTPException(status_code=413, detail="Pasted text is too large")

    # Generate unique document ID
    doc_id = str(uuid.uuid4())[:12]

    # Preprocess text
    cleaned_text = preprocess(text)

    # Store document metadata (no file saved)
    documents[doc_id] = {
        "id": doc_id,
        "filename": filename,
        "file_path": None,
        "text": cleaned_text,
        "page_count": 0,
        "char_count": len(cleaned_text),
        "format": "text",
    }

    return UploadResponse(
        document_id=doc_id,
        filename=filename,
        page_count=0,
        char_count=len(cleaned_text),
        status="uploaded",
    )
