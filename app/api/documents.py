from fastapi import APIRouter, HTTPException, Depends
from app.auth.dependencies import get_current_user
from app.services.document_manager import get_all_documents, get_document, delete_document_record, delete_uploaded_pdf
from app.rag.vector_store import delete_document_vectors

documents_router = APIRouter()

@documents_router.get("/documents")
def list_documents(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    documents = get_all_documents(user_id)
    return {
        "total_documents": len(documents),
        "documents": documents
    }

@documents_router.get("/documents/{document_id}")
def get_document_by_id(document_id: str, current_user: dict = Depends(get_current_user)):
    document = get_document(document_id)
    if document is None or document.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )
    return document

from fastapi.responses import FileResponse
import os

@documents_router.get("/documents/{document_id}/download")
def download_document(document_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    document = get_document(document_id)
    if document is None or document.get("user_id") != user_id:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )
    file_path = f"uploads/{user_id}/{document_id}.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="PDF file not found on disk."
        )
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=document["filename"]
    )

@documents_router.delete("/documents")
def clear_all_documents(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    documents = get_all_documents(user_id)
    
    for doc in documents:
        document_id = doc["document_id"]
        delete_document_vectors(document_id)
        delete_uploaded_pdf(user_id, document_id)
        delete_document_record(document_id)
        
    return {"message": "All documents cleared successfully."}

@documents_router.delete("/documents/{document_id}")
def remove_document(document_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    document = get_document(document_id)
    
    if document is None or document.get("user_id") != user_id:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # Delete vectors from Chroma
    delete_document_vectors(document_id)

    # Delete uploaded PDF
    delete_uploaded_pdf(user_id, document_id)

    # Delete SQLite record
    delete_document_record(document_id)

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
    }