from app.models.llm import model
from app.prompts.prompts import rag_prompt

stream_chain = rag_prompt | model