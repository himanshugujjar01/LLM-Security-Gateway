from fastapi import APIRouter
from app.dashboard.metrics import metrics

router = APIRouter()

@router.get("/security-dashboard")
def security_dashboard():

    security_score = max(
    0,
    100 - (
        metrics["blocked_requests"] * 5
    )
)

    return {
        "security_score": security_score,
        
        "requests": {
            "total": metrics["total_requests"],
            "blocked": metrics["blocked_requests"]
        },
        "detections": {
            "prompt_injections": metrics["prompt_injections"],
            "pii_detected": metrics["pii_detected"],
            "threat_matches": metrics["threat_matches"]
        }
    }