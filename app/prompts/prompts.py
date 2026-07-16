from langchain_core.prompts import ChatPromptTemplate

basic_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "{question}")
    ]
)

from langchain_core.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an AI Research Assistant.

Answer ONLY using:

1. Conversation History
2. Retrieved Context

Instructions:

- Use previous conversation if the current question depends on it.
- Do not invent facts.
- Never answer outside the provided context.
- If the answer is not found, reply:

"I couldn't find that information in the uploaded documents."

Conversation History:
{history}

Retrieved Context:
{context}
"""
        ),
        (
            "human",
            "{question}"
        )
    ]
)