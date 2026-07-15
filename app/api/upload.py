from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vector_store import create_vector_store
from app.services.document_manager import calculate_file_hash

from app.services.document_manager import (
    calculate_file_hash,
    document_exists,
    insert_document,
)

from app.rag.vector_store import (
    create_vector_store
    
)
upload_router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@upload_router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        return {"error": "Only PDF files are allowed!"}

    # Save uploaded PDF
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Calculate SHA-256 hash
    file_hash = calculate_file_hash(file_path)

    if document_exists(file_hash):
        return {
            "message": "Document already indexed.",
            "filename": file.filename,
            "file_hash": file_hash,
        }

    # Load PDF
    documents = load_pdf(str(file_path))

    # Split into chunks
    chunks = split_documents(documents)

    # Generate unique document ID
    document_id = str(uuid4())

    # Attach metadata to every chunk
    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = file.filename
        chunk.metadata["document_id"] = document_id
        chunk.metadata["file_hash"] = file_hash
        chunk.metadata["chunk_id"] = i
        chunk.metadata["page"] = chunk.metadata.get("page", 0)

    # Store chunks in ChromaDB
    create_vector_store(chunks)

    insert_document(
        document_id=document_id,
        filename=file.filename,
        file_hash=file_hash,
        pages=len(documents),
        chunks=len(chunks),
    )

    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "document_id": document_id,
        "file_hash": file_hash,
        "chunks_created": len(chunks),
    }