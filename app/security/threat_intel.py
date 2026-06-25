THREAT_INDICATORS = [
    "ransomware",
    "malware",
    "phishing",
    "keylogger",
    "trojan",
    "backdoor",
    "credential theft",
    "data exfiltration",
    "exploit",
    "payload",
    "reverse shell"
]


def check_threat_intel(message: str):
    """
    Checks user message against known threat indicators.

    Returns dictionary because main.py expects:
    threat_result["is_threat"]
    threat_result["indicator"]
    """

    if not isinstance(message, str):
        message = str(message)

    message_lower = message.lower()

    for indicator in THREAT_INDICATORS:
        if indicator in message_lower:
            return {
                "is_threat": True,
                "indicator": indicator,
                "reason": "Threat Intelligence Match"
            }

    return {
        "is_threat": False,
        "indicator": None,
        "reason": "No threat detected"
    }