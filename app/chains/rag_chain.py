from app.rag import history
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

import uuid


chain = rag_prompt | model | StrOutputParser()


def ask_rag(question: str,session_id: str,document_id : str | None = None,k: int = 5):

    # Retrieve relevant chunks
    documents = retrieve_chunks(
        query=question,
        k=k,
        document_id=document_id,
    )

    history = get_conversation_history(session_id)

    history_text = build_history(history)

    # Build context
    context = build_context(documents)

    # Extract sources
    sources = extract_sources(documents)

    # Generate answer
    answer = chain.invoke(
        {
            "history": history_text,
            "context": context,
            "question": question,
        }
    )

    save_conversation(
        session_id,
        question,
        answer,
    )

    return {
        "answer": answer,
        "sources": sources
    }