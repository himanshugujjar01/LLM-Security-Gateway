def detect_prompt_injection(message: str):
    suspicious_keywords = [
        "ignore previous instructions",
        "bypass",
        "reveal system prompt",
        "developer mode",
        "jailbreak"
    ]

    for keyword in suspicious_keywords:
        if keyword.lower() in message.lower():
            return True

    return False