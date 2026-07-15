from fastapi import APIRouter

from app.services.document_manager import get_all_documents

documents_router = APIRouter()


@documents_router.get("/documents")
def list_documents():

    documents = get_all_documents()

    return {
        "total_documents": len(documents),
        "documents": documents
    }