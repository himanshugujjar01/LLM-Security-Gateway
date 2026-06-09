from fastapi import FastAPI
from pydantic import BaseModel

from app.security.pii_detector import detect_and_redact
from app.security.prompt_injection import detect_prompt_injection
from app.middleware.rate_limiter import RateLimiterMiddleware

app = FastAPI()
app.add_middleware(RateLimiterMiddleware)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {
        "message": "Enterprise LLM Security Gateway Running"
    }

@app.post("/chat")
def chat(request: ChatRequest):

    if detect_prompt_injection(request.message):
        return {
            "status": "blocked",
            "reason": "Prompt Injection Attempt Detected"
        }

    cleaned_message = detect_and_redact(request.message)

    return {
        "original": request.message,
        "redacted": cleaned_message
    }