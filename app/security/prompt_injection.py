import re


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"forget\s+(all\s+)?rules",
    r"bypass\s+(the\s+)?rules",
    r"bypass\s+(the\s+)?policy",
    r"disable\s+(all\s+)?safety",
    r"disable\s+(the\s+)?filter",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(the\s+)?system\s+prompt",
    r"print\s+(the\s+)?system\s+prompt",
    r"developer\s+mode",
    r"jailbreak\s+mode",
    r"act\s+as\s+DAN",
    r"do\s+anything\s+now",
    r"you\s+are\s+now\s+unrestricted",
    r"remove\s+(all\s+)?limitations",
    r"override\s+(the\s+)?instructions",
    r"override\s+(the\s+)?system",
    r"ignore\s+(the\s+)?developer\s+message",
    r"ignore\s+(the\s+)?system\s+message",
    r"hidden\s+instructions",
    r"confidential\s+instructions",
    r"reveal\s+your\s+rules",
    r"tell\s+me\s+your\s+rules",
]


SUSPICIOUS_KEYWORDS = [
    "jailbreak",
    "dan mode",
    "developer mode",
    "system prompt",
    "hidden prompt",
    "bypass",
    "override",
    "unrestricted",
    "ignore instructions",
    "disable safety",
    "no restrictions",
]


def analyze_prompt_injection(message: str):
    """
    Analyze user prompt for prompt injection attempts.

    Returns:
        dict:
            is_injection: bool
            risk_score: int
            matched_patterns: list
            reason: str
    """

    message_lower = message.lower()
    matched_patterns = []
    risk_score = 0

    # Heuristic regex detection
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            matched_patterns.append(pattern)
            risk_score += 25

    # Keyword-based scoring
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in message_lower:
            matched_patterns.append(keyword)
            risk_score += 10

    # Long suspicious instruction chains
    suspicious_instruction_words = [
        "ignore",
        "override",
        "bypass",
        "reveal",
        "disable",
        "forget",
        "unrestricted"
    ]

    for word in suspicious_instruction_words:
        if word in message_lower:
            risk_score += 5

    # Cap score at 100
    risk_score = min(risk_score, 100)

    is_injection = risk_score >= 25

    if is_injection:
        reason = "Prompt injection attempt detected"
    else:
        reason = "No prompt injection detected"

    return {
        "is_injection": is_injection,
        "risk_score": risk_score,
        "matched_patterns": list(set(matched_patterns)),
        "reason": reason
    }


def detect_prompt_injection(message: str) -> bool:
    """
    Backward-compatible function used by main.py.
    Returns True if prompt injection is detected.
    """

    result = analyze_prompt_injection(message)
    return result["is_injection"]