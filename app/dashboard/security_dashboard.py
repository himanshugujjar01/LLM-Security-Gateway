from fastapi import APIRouter
from app.dashboard.metrics import metrics

router = APIRouter()


@router.get("/security-dashboard")
def security_dashboard():
    total_requests = metrics.get("total_requests", 0)
    blocked_requests = metrics.get("blocked_requests", 0)

    security_score = max(
        0,
        100 - (blocked_requests * 5)
    )

    return {
        "security_score": security_score,
        "requests": {
            "total": total_requests,
            "blocked": blocked_requests
        },
        "detections": {
            "prompt_injections": metrics.get("prompt_injections", 0),
            "pii_detected": metrics.get("pii_detected", 0),
            "threat_matches": metrics.get("threat_matches", 0),
            "unsafe_outputs": metrics.get("unsafe_outputs", 0)
        }
    }