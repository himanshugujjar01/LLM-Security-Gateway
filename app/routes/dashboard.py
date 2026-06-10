from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
def security_stats():
    with open("app/logs/security.log", "r") as file:
        logs = file.readlines()

    prompt_injections = sum(
        1 for log in logs if "Prompt Injection" in log
    )

    return {
        "total_events": len(logs),
        "prompt_injections": prompt_injections
    }