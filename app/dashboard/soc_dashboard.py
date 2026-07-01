from fastapi import APIRouter
from app.dashboard.metrics import metrics

router = APIRouter()


def calculate_security_score(blocked_requests: int) -> int:
    score = 100 - (blocked_requests * 5)
    return max(0, score)


def calculate_risk_level(security_score: int) -> str:
    if security_score >= 90:
        return "LOW"
    elif security_score >= 70:
        return "MEDIUM"
    else:
        return "HIGH"


def calculate_percentage(value: int, total: int) -> float:
    if total == 0:
        return 0.0

    return round((value / total) * 100, 2)


def get_compliance_status(total_requests: int, blocked_requests: int) -> str:
    if total_requests == 0:
        return "NO TRAFFIC ANALYZED"

    if blocked_requests == 0:
        return "COMPLIANT - NO BLOCKED REQUESTS"

    return "MONITORING ACTIVE - SECURITY EVENTS DETECTED"


def get_soc_recommendations(risk_level: str, pii_detected: int, threat_matches: int):
    recommendations = []

    if risk_level == "LOW":
        recommendations.append(
            "Continue monitoring gateway traffic and maintain regular audit review."
        )

    if risk_level == "MEDIUM":
        recommendations.append(
            "Review blocked prompts and validate whether repeated suspicious activity is present."
        )

    if risk_level == "HIGH":
        recommendations.append(
            "Immediate SOC review is recommended due to high blocked activity."
        )

    if pii_detected > 0:
        recommendations.append(
            "Review PII detection events to ensure sensitive data is not being sent to LLM systems."
        )

    if threat_matches > 0:
        recommendations.append(
            "Investigate threat intelligence matches and confirm whether malicious intent exists."
        )

    if not recommendations:
        recommendations.append(
            "No immediate action required. Gateway monitoring is active."
        )

    return recommendations


@router.get("/soc-dashboard")
def soc_dashboard():
    total_requests = metrics.get("total_requests", 0)
    blocked_requests = metrics.get("blocked_requests", 0)
    allowed_requests = total_requests - blocked_requests

    prompt_injections = metrics.get("prompt_injections", 0)
    pii_detected = metrics.get("pii_detected", 0)
    threat_matches = metrics.get("threat_matches", 0)
    unsafe_outputs = metrics.get("unsafe_outputs", 0)

    security_score = calculate_security_score(blocked_requests)
    risk_level = calculate_risk_level(security_score)

    block_rate = calculate_percentage(
        blocked_requests,
        total_requests
    )

    pii_detection_rate = calculate_percentage(
        pii_detected,
        total_requests
    )

    compliance_status = get_compliance_status(
        total_requests,
        blocked_requests
    )

    recommendations = get_soc_recommendations(
        risk_level,
        pii_detected,
        threat_matches
    )

    return {
        "dashboard_name": "SOC Compliance Dashboard",
        "gateway_status": "ACTIVE",

        "security_overview": {
            "security_score": security_score,
            "risk_level": risk_level,
            "compliance_status": compliance_status
        },

        "request_summary": {
            "total_requests": total_requests,
            "allowed_requests": allowed_requests,
            "blocked_requests": blocked_requests,
            "block_rate_percent": block_rate
        },

        "detection_summary": {
            "prompt_injections": prompt_injections,
            "pii_detected": pii_detected,
            "threat_matches": threat_matches,
            "unsafe_outputs": unsafe_outputs,
            "pii_detection_rate_percent": pii_detection_rate
        },

        "compliance_controls": {
            "api_authentication": "ENABLED",
            "rate_limiting": "ENABLED",
            "audit_logging": "ENABLED",
            "pii_monitoring": "ENABLED",
            "threat_monitoring": "ENABLED",
            "database_logging": "ENABLED"
        },

        "soc_recommendations": recommendations
    }