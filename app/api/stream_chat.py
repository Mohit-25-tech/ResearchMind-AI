from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import uuid

from app.chains.rag_chain import stream_rag

stream_router = APIRouter()


@stream_router.post("/stream-chat")
def stream_chat(
    question: str,
    session_id: str | None = None,
    document_id: str | None = None,
):

    if session_id is None:
        session_id = str(uuid.uuid4())

    return StreamingResponse(
        stream_rag(
            question=question,
            session_id=session_id,
            document_id=document_id,
        ),
        media_type="text/plain",
    )