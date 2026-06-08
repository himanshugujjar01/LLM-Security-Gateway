from fastapi import FastAPI
from pydantic import BaseModel

from app.security.pii_detector import detect_and_redact

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {
        "message": "Enterprise LLM Security Gateway Running"
    }

@app.post("/chat")
def chat(request: ChatRequest):
    cleaned_message = detect_and_redact(request.message)

    return {
        "original": request.message,
        "redacted": cleaned_message
    }