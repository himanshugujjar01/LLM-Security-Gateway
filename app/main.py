from fastapi import FastAPI
from pydantic import BaseModel

from app.security.pii_detector import redact_pii
from app.security.prompt_injection import detect_prompt_injection
from app.middleware.rate_limiter import RateLimiterMiddleware
from fastapi import Depends
from app.auth.api_key import verify_api_key
from app.services.logger import logger
from app.dashboard.dashboard import router as dashboard_router
from app.routes.dashboard import router as dashboard_router
from app.security.output_filter import filter_response
from app.services.containment import isolate_host
from app.security.threat_intel import check_threat_intel
from app.services.alert_manager import send_alert

app = FastAPI()
app.include_router(dashboard_router, prefix="/dashboard")
app.add_middleware(RateLimiterMiddleware)
app.include_router(dashboard_router)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):

    # Prompt Injection Detection
    if detect_prompt_injection(request.message):

        send_alert(
            "PROMPT_INJECTION",
            request.message
        )

        logger.warning(
            f"Prompt Injection Attempt: {request.message}"
        )

        return {
            "status": "blocked",
            "reason": "Prompt Injection Attempt Detected"
        }

    # Threat Intelligence Detection
    threat_detected, indicator = check_threat_intel(
        request.message
    )

    if threat_detected:

        send_alert(
            "THREAT_INTEL_MATCH",
            indicator
        )

        logger.warning(
            f"Threat Intelligence Match: {indicator}"
        )

        return {
            "status": "blocked",
            "reason": "Threat Intelligence Match",
            "indicator": indicator
        }

    # PII Detection
   # PII Detection
    cleaned_message = redact_pii(request.message)

    print(type(cleaned_message))
    print(cleaned_message)

    if cleaned_message["original"] != cleaned_message["redacted"]:
        send_alert(
            "PII_DETECTED",
            request.message
        )

        logger.warning(
            f"PII Detected: {request.message}"
        )

    # Output Filtering
    safe_message = filter_response(
    cleaned_message["redacted"]
)
    logger.info("Request Processed Successfully")

    return {
        "original": request.message,
        "redacted": safe_message
    }