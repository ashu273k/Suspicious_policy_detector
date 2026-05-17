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
from api.schemas import UploadResponse

router = APIRouter()

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
    ext = Path(file.filename).suffix.lower()

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
    except Exception as e:
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
        "filename": file.filename,
        "file_path": str(file_path),
        "text": cleaned_text,
        "page_count": parsed["page_count"],
        "char_count": len(cleaned_text),
        "format": parsed["format"],
    }

    return UploadResponse(
        document_id=doc_id,
        filename=file.filename,
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
async def upload_text(payload: dict):
    """
    Upload raw contract text (paste). Expects JSON: {"text": "...", "filename": "optional name"}
    """
    text = payload.get("text")
    filename = payload.get("filename", "pasted_contract.txt")

    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="No contract text provided")

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
