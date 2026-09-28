from langchain_core.output_parsers import StrOutputParser
from app.models.llm import model
from app.prompts.prompts import rag_prompt
from app.rag.retriver import retrieve_chunks
from app.rag.hybrid_retriever import retrieve as hybrid_retrieve
from app.rag.context import build_context
from app.rag.sources import extract_sources
from app.rag.history import build_history
from app.config.settings import settings
from app.services.conversation_manager import (
    get_conversation_history,
    save_conversation,
)

chain = rag_prompt | model | StrOutputParser()
stream_chain = rag_prompt | model


def _get_retrieved_documents(
    question: str,
    user_id: int,
    document_ids: list[str] | str | None = None,
    document_id: str | None = None,
    k: int = 5,
):
    """
    Retrieve documents based on feature flags (hybrid + rerank vs baseline MMR).
    """
    target_ids = document_ids if document_ids is not None else document_id
    if settings.use_hybrid:
        mode = "hybrid_rerank" if settings.use_reranker else "hybrid"
        return hybrid_retrieve(
            query=question,
            user_id=user_id,
            document_ids=target_ids,
            mode=mode,
        )
    return retrieve_chunks(
        query=question,
        user_id=user_id,
        k=k,
        document_id=target_ids,
    )


def ask_rag(
    question: str,
    conversation_id: int,
    user_id: int,
    document_ids: list[str] | str | None = None,
    document_id: str | None = None,
    k: int = 5,
):
    """
    Standard (non-streaming) RAG response.
    """
    target_ids = document_ids if document_ids is not None else document_id
    documents = _get_retrieved_documents(
        question=question,
        user_id=user_id,
        document_ids=target_ids,
        k=k,
    )

    # Conversation history
    history = get_conversation_history(conversation_id)
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

    # Save conversation messages
    save_conversation(
        conversation_id=conversation_id,
        question=question,
        answer=answer,
    )

    return {
        "answer": answer,
        "sources": sources,
    }


def stream_rag(
    question: str,
    conversation_id: int,
    user_id: int,
    document_ids: list[str] | str | None = None,
    document_id: str | None = None,
    k: int = 5,
):
    """
    Streaming RAG response.
    """
    target_ids = document_ids if document_ids is not None else document_id
    documents = _get_retrieved_documents(
        question=question,
        user_id=user_id,
        document_ids=target_ids,
        k=k,
    )

    # Conversation history
    history = get_conversation_history(conversation_id)
    history_text = build_history(history)

    # Context
    context = build_context(documents)

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

    # Save conversation messages after streaming completes
    save_conversation(
        conversation_id=conversation_id,
        question=question,
        answer=complete_answer,
    )