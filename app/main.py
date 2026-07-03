from fastapi import FastAPI, Header
from pydantic import BaseModel

from app.auth.api_key import verify_api_key
from app.middleware.rate_limiter import RateLimiterMiddleware

from app.security.pii_detector import redact_pii
from app.security.presidio_detector import presidio_redact
from app.security.prompt_injection import detect_prompt_injection
from app.security.threat_intel import check_threat_intel
from app.security.output_filter import filter_response, check_response_safety
from app.security.anonymizer import anonymize_text, deanonymize_text
from app.security.custom_sensitive_detector import detect_custom_sensitive_data

from app.services.logger import logger
from app.services.alert_manager import send_alert
from app.services.db_logger import log_prompt_to_db
from app.services.llm_client import call_llm_async

from app.dashboard.dashboard import router as dashboard_router
from app.dashboard.metrics import router as metrics_router
from app.dashboard.metrics import metrics
from app.dashboard.log_analyzer import router as log_router
from app.dashboard.security_dashboard import router as security_dashboard_router
from app.dashboard.report_export import router as report_router
from app.dashboard.event_history import router as history_router
from app.dashboard.soc_dashboard import router as soc_dashboard_router
from app.routes.rbac_routes import router as rbac_router


app = FastAPI()

app.add_middleware(RateLimiterMiddleware)

app.include_router(dashboard_router, prefix="/dashboard")
app.include_router(metrics_router)
app.include_router(log_router)
app.include_router(security_dashboard_router)
app.include_router(report_router)
app.include_router(history_router)
app.include_router(soc_dashboard_router)
app.include_router(rbac_router)


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(request: ChatRequest, x_api_key: str = Header(None)):
    metrics["total_requests"] += 1

    verify_api_key(x_api_key)

    # 1. Prompt Injection Detection
    if detect_prompt_injection(request.message):
        metrics["blocked_requests"] += 1
        metrics["prompt_injections"] += 1

        send_alert("PROMPT_INJECTION", request.message)

        logger.warning(
            f"Prompt Injection Attempt: {request.message}"
        )

        log_prompt_to_db(
            user_message=request.message,
            redacted_message=request.message,
            response_text="Blocked by prompt injection detection",
            status="blocked",
            detection_type="PROMPT_INJECTION"
        )

        return {
            "status": "blocked",
            "reason": "Prompt Injection Attempt Detected"
        }

    # 2. Threat Intelligence Check
    threat_result = check_threat_intel(request.message)

    if threat_result["is_threat"]:
        metrics["blocked_requests"] += 1
        metrics["threat_matches"] += 1

        send_alert("THREAT_INTEL_MATCH", request.message)

        logger.warning(
            f"Threat Intelligence Match: {threat_result['indicator']}"
        )

        log_prompt_to_db(
            user_message=request.message,
            redacted_message=request.message,
            response_text="Blocked by threat intelligence",
            status="blocked",
            detection_type="THREAT_INTEL_MATCH"
        )

        return {
            "status": "blocked",
            "reason": "Threat Intelligence Match",
            "indicator": threat_result["indicator"]
        }

    # 3. PII Detection using Microsoft Presidio
    cleaned_message = presidio_redact(request.message)

    # 4. Regex fallback PII detection
    if cleaned_message["original"] == cleaned_message["redacted"]:
        cleaned_message = redact_pii(request.message)

    cleaned_message.setdefault("entities_found", [])

    # 5. Custom sensitive data detection
    custom_sensitive_result = detect_custom_sensitive_data(
        cleaned_message["redacted"]
    )

    if custom_sensitive_result["original"] != custom_sensitive_result["redacted"]:
        cleaned_message["redacted"] = custom_sensitive_result["redacted"]

        cleaned_message["entities_found"].extend(
            custom_sensitive_result["entities_found"]
        )

    # 6. PII metric and alert
    if cleaned_message["original"] != cleaned_message["redacted"]:
        metrics["pii_detected"] += 1

        send_alert(
            "PII_DETECTED",
            request.message
        )

        logger.warning(
            f"PII Detected and Redacted: {request.message}"
        )

    # 7. Anonymization
    anonymized_text, mapping = anonymize_text(
        cleaned_message["redacted"]
    )

    # 8. Filter safe prompt before LLM
    safe_message = filter_response(
        anonymized_text
    )

    # 9. Send prompt to LLM client
    llm_response = await call_llm_async(
    safe_message
)

    print("DEBUG LLM RESPONSE:", llm_response)

    # 10. Check generated LLM response
    safety_result = check_response_safety(
        llm_response
    )

    print("DEBUG SAFETY RESULT:", safety_result)

    # 11. Block unsafe generated output
    if not safety_result["is_safe"]:
        metrics["blocked_requests"] += 1
        metrics["unsafe_outputs"] = metrics.get("unsafe_outputs", 0) + 1

        send_alert(
            "UNSAFE_OUTPUT",
            safety_result["reason"]
        )

        logger.warning(
            f"Unsafe generated response blocked: {safety_result['matched_policy']}"
        )

        log_prompt_to_db(
            user_message=request.message,
            redacted_message=cleaned_message["redacted"],
            response_text=safety_result["filtered_response"],
            status="blocked",
            detection_type="UNSAFE_OUTPUT"
        )

        return {
            "status": "blocked",
            "reason": "Unsafe generated response blocked by content safety filter",
            "matched_policy": safety_result["matched_policy"]
        }

    # 12. Deanonymize safe response
    final_response = deanonymize_text(
        safety_result["filtered_response"],
        mapping
    )

    # 13. PostgreSQL allowed request logging
    log_prompt_to_db(
        user_message=request.message,
        redacted_message=cleaned_message["redacted"],
        response_text=final_response,
        status="allowed",
        detection_type="PII_CHECK"
    )

    logger.info("Request Processed Successfully")

    return {
        "response": final_response
    }