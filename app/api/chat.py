from fastapi import APIRouter

from app.chains.rag_chain import ask_rag

chat_router = APIRouter()


@chat_router.post("/chat")
def chat(question: str):

    answer = ask_rag(question)

    return {
        "answer": answer
    }
