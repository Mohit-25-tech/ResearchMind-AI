from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vector_store import create_vector_store

docs = load_pdf("uploads/docker.pdf")
chunks = split_documents(docs)

create_vector_store(chunks)

print("Success")