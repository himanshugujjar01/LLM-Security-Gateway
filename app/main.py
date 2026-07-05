from fastapi import FastAPI, Header
from pydantic import BaseModel

from app.auth.api_key import verify_api_key
from app.auth.rbac import check_model_access
from app.middleware.rate_limiter import RateLimiterMiddleware

from app.security.pii_detector import redact_pii
from app.security.presidio_detector import presidio_redact
from app.security.prompt_injection import detect_prompt_injection
from app.security.rebuff_guard import rebuff_style_check
from app.security.threat_intel import check_threat_intel
from app.security.output_filter import filter_response, check_response_safety
from app.security.anonymizer import anonymize_text, deanonymize_text
from app.security.custom_sensitive_detector import detect_custom_sensitive_data
from app.security.phi_detector import detect_phi, redact_phi

from app.services.logger import logger
from app.services.alert_manager import send_alert
from app.services.db_logger import log_prompt_to_db
from app.services.llm_client import call_llm
from app.services.semantic_cache import get_cached_response, set_cached_response

from app.dashboard.dashboard import router as dashboard_router
from app.dashboard.metrics import router as metrics_router
from app.dashboard.metrics import metrics
from app.dashboard.log_analyzer import router as log_router
from app.dashboard.security_dashboard import router as security_dashboard_router
from app.dashboard.report_export import router as report_router
from app.dashboard.event_history import router as history_router
from app.dashboard.soc_dashboard import router as soc_dashboard_router
from app.routes.rbac_routes import router as rbac_router


app = FastAPI(
    title="LLM Security Gateway",
    description="Enterprise LLM and GenAI Security Gateway",
    version="1.0.0"
)

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
    model_name: str = "general-llm"


@app.post("/chat")
def chat(request: ChatRequest, x_api_key: str = Header(None)):
    metrics["total_requests"] += 1

    verify_api_key(x_api_key)

    # RBAC model access check
    rbac_result = check_model_access(
        api_key=x_api_key,
        requested_model=request.model_name
    )

    if not rbac_result["allowed"]:
        metrics["blocked_requests"] += 1
        metrics["rbac_denied"] = metrics.get("rbac_denied", 0) + 1

        logger.warning(
            f"RBAC Access Denied: {rbac_result['reason']} | Model: {request.model_name}"
        )

        log_prompt_to_db(
            user_message=request.message,
            redacted_message=request.message,
            response_text=f"RBAC denied for model: {request.model_name}",
            status="blocked",
            detection_type="RBAC_DENIED"
        )

        return {
            "status": "blocked",
            "reason": "RBAC access denied",
            "requested_model": request.model_name,
            "details": rbac_result
        }

    # Basic prompt injection detection
    if detect_prompt_injection(request.message):
        metrics["blocked_requests"] += 1
        metrics["prompt_injections"] += 1

        send_alert(
            "PROMPT_INJECTION",
            request.message
        )

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

    # Advanced Rebuff-style prompt injection detection
    rebuff_result = rebuff_style_check(request.message)

    if rebuff_result["blocked"]:
        metrics["blocked_requests"] += 1
        metrics["advanced_prompt_injections"] = metrics.get(
            "advanced_prompt_injections",
            0
        ) + 1

        send_alert(
            "ADVANCED_PROMPT_INJECTION",
            str(rebuff_result)
        )

        logger.warning(
            f"Advanced Prompt Injection Blocked: {rebuff_result}"
        )

        log_prompt_to_db(
            user_message=request.message,
            redacted_message=request.message,
            response_text="Blocked by Rebuff-style prompt injection detection",
            status="blocked",
            detection_type="ADVANCED_PROMPT_INJECTION"
        )

        return {
            "status": "blocked",
            "reason": "Advanced prompt injection detected",
            "details": rebuff_result
        }

    # Threat intelligence check
    threat_result = check_threat_intel(request.message)

    if threat_result["is_threat"]:
        metrics["blocked_requests"] += 1
        metrics["threat_matches"] += 1

        send_alert(
            "THREAT_INTEL_MATCH",
            request.message
        )

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

    # PII detection using Microsoft Presidio
    cleaned_message = presidio_redact(request.message)

    # Regex fallback PII detection
    if cleaned_message["original"] == cleaned_message["redacted"]:
        cleaned_message = redact_pii(request.message)

    cleaned_message.setdefault("entities_found", [])

    # Custom sensitive data detection
    custom_sensitive_result = detect_custom_sensitive_data(
        cleaned_message["redacted"]
    )

    if custom_sensitive_result["original"] != custom_sensitive_result["redacted"]:
        cleaned_message["redacted"] = custom_sensitive_result["redacted"]

        cleaned_message["entities_found"].extend(
            custom_sensitive_result["entities_found"]
        )

    if cleaned_message["original"] != cleaned_message["redacted"]:
        metrics["pii_detected"] += 1

        send_alert(
            "PII_DETECTED",
            request.message
        )

        logger.warning(
            f"PII Detected and Redacted: {request.message}"
        )

    # PHI detection
    phi_result = detect_phi(
        cleaned_message["redacted"]
    )

    if phi_result["phi_detected"]:
        metrics["phi_detected"] = metrics.get("phi_detected", 0) + 1

        cleaned_message["redacted"] = redact_phi(
            cleaned_message["redacted"]
        )

        send_alert(
            "PHI_DETECTED",
            str(phi_result)
        )

        logger.warning(
            f"PHI Detected and Redacted: {phi_result}"
        )

    # Anonymization
    anonymized_text, mapping = anonymize_text(
        cleaned_message["redacted"]
    )

    # Filter prompt secrets before LLM
    safe_message = filter_response(
        anonymized_text
    )

    # Semantic cache check
    cached_result = get_cached_response(
        prompt=safe_message,
        model_name=request.model_name
    )

    if cached_result:
        metrics["semantic_cache_hits"] = metrics.get(
            "semantic_cache_hits",
            0
        ) + 1

        return {
            "response": cached_result["response"],
            "model_used": request.model_name,
            "cache_status": "HIT",
            "cache_type": cached_result.get("cache_type"),
            "similarity_score": cached_result.get("similarity_score")
        }

    metrics["semantic_cache_misses"] = metrics.get(
        "semantic_cache_misses",
        0
    ) + 1

    # LLM provider proxy
    metrics["real_llm_proxy_requests"] = metrics.get(
        "real_llm_proxy_requests",
        0
    ) + 1

    llm_response = call_llm(
        prompt=safe_message,
        model_name=request.model_name
    )

    # Generated response safety check
    safety_result = check_response_safety(
        llm_response
    )

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

    # Deanonymization
    final_response = deanonymize_text(
        safety_result["filtered_response"],
        mapping
    )

    # Cache safe final response
    set_cached_response(
        prompt=safe_message,
        response=final_response,
        model_name=request.model_name
    )

    # PostgreSQL logging
    log_prompt_to_db(
        user_message=request.message,
        redacted_message=cleaned_message["redacted"],
        response_text=final_response,
        status="allowed",
        detection_type="PII_PHI_CHECK"
    )

    logger.info(
        "Request Processed Successfully"
    )

    return {
        "response": final_response,
        "model_used": request.model_name,
        "cache_status": "MISS"
    }