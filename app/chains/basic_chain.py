from langchain_core.output_parsers import StrOutputParser

from app.models.llm import model
from app.prompts.prompts import basic_prompt

basic_chain = basic_prompt | model | StrOutputParser()

