from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/log-summary")
def log_summary():

    summary = {
        "prompt_injections": 0,
        "pii_detected": 0,
        "threat_matches": 0
    }

    log_file = os.path.join("app", "logs", "security.log")

    try:
        with open(log_file, "r") as file:
            logs = file.readlines()

        for line in logs:
            if "Prompt Injection" in line:
                summary["prompt_injections"] += 1

            if "PII Detected" in line:
                summary["pii_detected"] += 1

            if "Threat Intelligence Match" in line:
                summary["threat_matches"] += 1

    except FileNotFoundError:
        return {"error": "security.log not found"}

    return summary