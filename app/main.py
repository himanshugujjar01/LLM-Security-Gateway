from fastapi import FastAPI
from pydantic import BaseModel

from app.security.pii_detector import redact_pii
from app.security.prompt_injection import detect_prompt_injection
from app.middleware.rate_limiter import RateLimiterMiddleware
from fastapi import Depends
from app.auth.api_key import verify_api_key
from app.services.logger import logger
from app.dashboard.dashboard import router as dashboard_router
from app.security.output_filter import filter_response
from app.services.containment import isolate_host
from app.security.threat_intel import check_threat_intel
from app.services.alert_manager import send_alert
from app.dashboard.metrics import router as metrics_router
from app.dashboard.metrics import metrics
from app.security.anonymizer import (
    anonymize_text,
    deanonymize_text
)
from app.dashboard.log_analyzer import router as log_router
from app.dashboard.security_dashboard import router as security_dashboard_router
from app.dashboard.report_export import router as report_router
from app.dashboard.event_history import router as history_router

app = FastAPI()
app.include_router(dashboard_router, prefix="/dashboard")
app.add_middleware(RateLimiterMiddleware)
app.include_router(dashboard_router)
app.include_router(metrics_router)
app.include_router(log_router)
app.include_router(security_dashboard_router)
app.include_router(report_router)
app.include_router(history_router)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):

    metrics["total_requests"] += 1

    # Prompt Injection Detection
    if detect_prompt_injection(request.message):

        metrics["prompt_injections"] += 1
        metrics["blocked_requests"] += 1

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

        metrics["threat_matches"] += 1
        metrics["blocked_requests"] += 1

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
    cleaned_message = redact_pii(request.message)
    anonymized_text, mapping = anonymize_text(
    cleaned_message["redacted"]
)

    print(type(cleaned_message))
    print(cleaned_message)

    if cleaned_message["original"] != cleaned_message["redacted"]:

        metrics["pii_detected"] += 1

        send_alert(
            "PII_DETECTED",
            request.message
        )

        logger.warning(
            f"PII Detected: {request.message}"
        )

    # Output Filtering
    safe_message = filter_response(
    anonymized_text
)
    llm_response = f"LLM received: {safe_message}"
    final_response = deanonymize_text(
    llm_response,
    mapping
)

    logger.info("Request Processed Successfully")

    return {
    "response": final_response
}