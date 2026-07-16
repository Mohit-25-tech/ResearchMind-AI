from fastapi import APIRouter
import uuid

from app.chains.rag_chain import ask_rag

chat_router = APIRouter()


@chat_router.post("/chat")
def chat(
    question: str,
    session_id: str | None = None,
    document_id: str | None = None,
):
    """
    Chat endpoint.

    document_id:
        None -> Search all uploaded documents
        Value -> Search only that document
    """

    if session_id is None:
        session_id = str(uuid.uuid4())

    response = ask_rag(
        question=question,
        session_id=session_id,
        document_id=document_id,
    )

    return {
        "session_id": session_id,
        **response,
    }