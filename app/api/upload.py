from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vector_store import create_vector_store
from app.services.document_manager import (
    calculate_file_hash,
    document_exists,
    insert_document,
)

upload_router = APIRouter()

UPLOAD_DIR = Path("uploads")

@upload_router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        return {"error": "Only PDF files are allowed!"}

    user_id = current_user["id"]
    user_upload_dir = UPLOAD_DIR / str(user_id)
    user_upload_dir.mkdir(exist_ok=True, parents=True)

    # Temporary file for hash calculation and loading
    temp_path = user_upload_dir / f"temp_{uuid4()}.pdf"
    
    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        file_hash = calculate_file_hash(temp_path)

        if document_exists(user_id, file_hash):
            temp_path.unlink()
            return {
                "message": "Document already indexed.",
                "filename": file.filename,
                "file_hash": file_hash,
            }

        # Generate unique document ID
        document_id = str(uuid4())

        # Rename temp file to document_id.pdf
        file_path = user_upload_dir / f"{document_id}.pdf"
        temp_path.rename(file_path)

        # Load PDF
        documents = load_pdf(str(file_path))

        # Split into chunks
        chunks = split_documents(documents)

        # Attach metadata to every chunk, including user_id
        for i, chunk in enumerate(chunks):
            chunk.metadata["source"] = file.filename
            chunk.metadata["document_id"] = document_id
            chunk.metadata["file_hash"] = file_hash
            chunk.metadata["chunk_id"] = i
            chunk.metadata["page"] = chunk.metadata.get("page", 0)
            chunk.metadata["user_id"] = user_id

        # Store chunks in ChromaDB
        create_vector_store(chunks)

        insert_document(
            document_id=document_id,
            filename=file.filename,
            file_hash=file_hash,
            pages=len(documents),
            chunks=len(chunks),
            user_id=user_id,
        )

        return {
            "message": "PDF uploaded successfully",
            "filename": file.filename,
            "document_id": document_id,
            "file_hash": file_hash,
            "chunks_created": len(chunks),
        }
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise e