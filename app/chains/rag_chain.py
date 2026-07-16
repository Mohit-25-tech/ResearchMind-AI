from langchain_core.output_parsers import StrOutputParser

from app.models.llm import model
from app.prompts.prompts import rag_prompt

from app.rag.retriver import retrieve_chunks
from app.rag.context import build_context
from app.rag.sources import extract_sources
from app.rag.history import build_history

from app.services.conversation_manager import (
    get_conversation_history,
    save_conversation,
)


# -----------------------------
# Normal RAG Chain
# -----------------------------
chain = rag_prompt | model | StrOutputParser()

# -----------------------------
# Streaming RAG Chain
# -----------------------------
stream_chain = rag_prompt | model


def ask_rag(
    question: str,
    session_id: str,
    document_id: str | None = None,
    k: int = 5,
):
    """
    Standard (non-streaming) RAG response.
    """

    # Retrieve documents
    documents = retrieve_chunks(
        query=question,
        k=k,
        document_id=document_id,
    )

    # Conversation history
    history = get_conversation_history(session_id)
    history_text = build_history(history)

    # Context
    context = build_context(documents)

    # Sources
    sources = extract_sources(documents)

    # Generate answer
    answer = chain.invoke(
        {
            "history": history_text,
            "context": context,
            "question": question,
        }
    )

    # Save conversation
    save_conversation(
        session_id=session_id,
        question=question,
        answer=answer,
    )

    return {
        "answer": answer,
        "sources": sources,
    }


def stream_rag(
    question: str,
    session_id: str,
    document_id: str | None = None,
    k: int = 5,
):
    """
    Streaming RAG response.
    """

    # Retrieve documents
    documents = retrieve_chunks(
        query=question,
        k=k,
        document_id=document_id,
    )

    # Conversation history
    history = get_conversation_history(session_id)
    history_text = build_history(history)

    # Context
    context = build_context(documents)

    # Sources
    sources = extract_sources(documents)

    complete_answer = ""

    for chunk in stream_chain.stream(
        {
            "history": history_text,
            "context": context,
            "question": question,
        }
    ):

        if chunk.content:
            complete_answer += chunk.content
            yield chunk.content

    # Save conversation after streaming finishes
    save_conversation(
        session_id=session_id,
        question=question,
        answer=complete_answer,
    )