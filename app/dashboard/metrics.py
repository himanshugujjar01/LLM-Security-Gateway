from fastapi import APIRouter

router = APIRouter()

metrics = {
    "total_requests": 0,
    "blocked_requests": 0,
    "prompt_injections": 0,
    "threat_matches": 0,
    "pii_detected": 0,
    "unsafe_outputs": 0,
    "rbac_denied": 0
}


@router.get("/metrics")
def get_metrics():
    return metrics