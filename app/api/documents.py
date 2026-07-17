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