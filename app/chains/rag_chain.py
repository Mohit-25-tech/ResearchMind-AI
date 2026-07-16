from langchain_core.output_parsers import StrOutputParser

from app.models.llm import model
from app.prompts.prompts import rag_prompt

from app.rag.retriver import retrieve_chunks
from app.rag.context import build_context
from app.rag.sources import extract_sources


chain = rag_prompt | model | StrOutputParser()


def ask_rag(question: str, k: int = 5):

    # Retrieve relevant chunks
    documents = retrieve_chunks(question, k)

    # Build context
    context = build_context(documents)

    # Extract sources
    sources = extract_sources(documents)

    # Generate answer
    answer = chain.invoke(
        {
            "context": context,
            "question": question
        }
    )

    return {
        "answer": answer,
        "sources": sources
    }