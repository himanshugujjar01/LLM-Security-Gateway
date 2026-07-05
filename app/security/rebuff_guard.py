import re


INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"forget\s+all\s+instructions",
    r"disregard\s+the\s+above",
    r"bypass\s+policy",
    r"bypass\s+security",
    r"disable\s+safety",
    r"jailbreak",
    r"developer\s+mode",
    r"system\s+prompt",
    r"reveal\s+your\s+instructions",
    r"reveal\s+system\s+prompt",
    r"act\s+as\s+dan",
    r"do\s+anything\s+now",
    r"no\s+restrictions",
    r"override\s+security",
    r"override\s+instructions",
    r"prompt\s+injection"
]


SUSPICIOUS_PHRASES = [
    "ignore previous instructions",
    "reveal system prompt",
    "bypass the filter",
    "disable safety",
    "show hidden instructions",
    "you are now in developer mode",
    "act as dan",
    "do anything now"
]


def rebuff_style_check(prompt: str):
    """
    Rebuff-style heuristic prompt injection detection.
    Gives a risk score and blocks high-risk prompts.
    """

    if not isinstance(prompt, str):
        prompt = str(prompt)

    score = 0
    matched_rules = []
    prompt_lower = prompt.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            score += 25
            matched_rules.append(pattern)

    for phrase in SUSPICIOUS_PHRASES:
        if phrase in prompt_lower:
            score += 20
            matched_rules.append(phrase)

    if len(prompt) > 1500:
        score += 10
        matched_rules.append("Unusually long prompt")

    blocked = score >= 40

    return {
        "blocked": blocked,
        "score": score,
        "matched_rules": list(set(matched_rules)),
        "reason": "Advanced prompt injection pattern detected"
        if blocked
        else "No advanced prompt injection detected"
    }