from pathlib import Path

from fastapi import APIRouter  ,File , UploadFile

from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vector_store import create_vector_store
from uuid import uuid4


upload_router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@upload_router.post("/upload")
async def upload_pdf(file : UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error":"Only pdf files are allowed!"}

    file_path = UPLOAD_DIR / file.filename

    with open(file_path , "wb") as f:
        f.write(await file.read())

    documents = load_pdf(str(file_path))

    chunks = split_documents(documents)

    document_id = str(uuid4())

    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = file.filename
        chunk.metadata["document_id"] = document_id
        chunk.metadata["chunk_id"]=i
        chunk.metadata["page"] = chunk.metadata.get("page", 0)

    
    create_vector_store(chunks)

    return {
        "message":"PDF uploaded successfully",
        "filename":file.filename,
        "chunks_created":len(chunks)
    }


        
