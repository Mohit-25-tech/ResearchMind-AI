from langchain_groq import ChatGroq
from dotenv import load_dotenv
from app.config.settings import settings

load_dotenv()

model = ChatGroq(
    model_name=settings.groq_model,
    max_retries=3,
    request_timeout=60.0,
)