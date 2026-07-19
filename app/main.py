import sys
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from app.api.chat import chat_router
from app.api.upload import upload_router
from app.services.database import initialize_database
from app.api.documents import documents_router
from app.api.stream_chat import stream_router
from app.auth.router import router as auth_router
from app.api.conversations import conversations_router

app = FastAPI()

# Run database setup and migrations
initialize_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://research-mind-ai-dun.vercel.app",
        "https://research-mind-ai-git-main-mohit-25-techs-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(documents_router)
app.include_router(stream_router)


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
