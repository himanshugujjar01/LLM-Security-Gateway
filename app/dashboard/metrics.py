from fastapi import APIRouter

router = APIRouter()

metrics = {
    "total_requests": 0,
    "blocked_requests": 0,
    "prompt_injections": 0,
    "advanced_prompt_injections": 0,
    "threat_matches": 0,
    "pii_detected": 0,
    "phi_detected": 0,
    "unsafe_outputs": 0,
    "rbac_denied": 0,
    "semantic_cache_hits": 0,
    "semantic_cache_misses": 0,
    "real_llm_proxy_requests": 0
}


@router.get("/metrics")
def get_metrics():
    return metrics