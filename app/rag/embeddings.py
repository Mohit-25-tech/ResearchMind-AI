import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_embedding_function():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )