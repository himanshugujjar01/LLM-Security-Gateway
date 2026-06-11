MALICIOUS_KEYWORDS = [
    "malware",
    "ransomware",
    "steal credentials",
    "bypass security",
    "keylogger"
]

def check_threat_intel(message: str):
    for keyword in MALICIOUS_KEYWORDS:
        if keyword.lower() in message.lower():
            return True, keyword

    return False, None