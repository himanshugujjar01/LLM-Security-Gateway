from fastapi import APIRouter
from app.dashboard.metrics import metrics

router = APIRouter()


@router.get("/soc-dashboard")
def soc_dashboard():
    total_requests = metrics.get("total_requests", 0)
    blocked_requests = metrics.get("blocked_requests", 0)
    allowed_requests = total_requests - blocked_requests

    security_score = max(
        0,
        100 - (blocked_requests * 5)
    )

    return {
        "dashboard_name": "SOC Compliance Dashboard",
        "gateway_status": "ACTIVE",

        "security_score": security_score,

        "request_summary": {
            "total_requests": total_requests,
            "allowed_requests": allowed_requests,
            "blocked_requests": blocked_requests
        },

        "detection_summary": {
            "prompt_injections": metrics.get("prompt_injections", 0),
            "pii_detected": metrics.get("pii_detected", 0),
            "threat_matches": metrics.get("threat_matches", 0),
            "unsafe_outputs": metrics.get("unsafe_outputs", 0)
        },

        "compliance_monitoring": {
            "audit_logging": "ENABLED",
            "pii_monitoring": "ENABLED",
            "threat_monitoring": "ENABLED",
            "rate_limiting": "ENABLED"
        },

        "soc_note": "This dashboard helps SOC analysts monitor LLM gateway activity, blocked prompts, sensitive data detections, and security events."
    }