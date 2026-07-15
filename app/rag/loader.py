from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

def load_pdf(file_path:str):
    """Load a pdf from disk and returns alist of document object"""
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents