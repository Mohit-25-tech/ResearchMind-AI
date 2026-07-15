from fastapi import APIRouter
from fastapi import HTTPException
from app.services.document_manager import get_all_documents
from app.services.document_manager import get_document, delete_document_record
from app.rag.vector_store import delete_document_vectors
from app.services.document_manager import delete_uploaded_pdf
documents_router = APIRouter()


@documents_router.get("/documents")
def list_documents():

    documents = get_all_documents()

    return {
        "total_documents": len(documents),
        "documents": documents
    }

@documents_router.get("/documents/{document_id}")
def get_document_by_id(document_id: str):

    document = get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return document

@documents_router.delete("/documents/{document_id}")
def remove_document(document_id: str):

    document = get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # Delete vectors from Chroma
    delete_document_vectors(document_id)

    # Delete uploaded PDF
    delete_uploaded_pdf(document["filename"])

    # Delete SQLite record
    delete_document_record(document_id)

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
    }