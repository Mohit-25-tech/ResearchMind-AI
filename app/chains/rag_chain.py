from langchain_core.output_parsers import StrOutputParser

from app.models.llm import model
from app.prompts.prompts import rag_prompt
from app.rag.retriver import get_relevant_chunks


def ask_rag(question: str):

    docs = get_relevant_chunks(question)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    chain = rag_prompt | model | StrOutputParser()

    return chain.invoke(
        {
            "context":context,
            "question":question
        }
    )
    