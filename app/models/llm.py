from langchain_groq import ChatGroq
from dotenv import load_dotenv
from app.config.settings import settings

load_dotenv()

model = ChatGroq(model_name=settings.groq_model)