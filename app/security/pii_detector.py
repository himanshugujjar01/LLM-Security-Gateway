import re

def detect_and_redact(text: str):
    redacted = text

    # Email
    redacted = re.sub(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        '[EMAIL]',
        redacted
    )

    # Phone Number (10 digits)
    redacted = re.sub(
        r'\b\d{10}\b',
        '[PHONE]',
        redacted
    )

    # Aadhaar Number (12 digits)
    redacted = re.sub(
        r'\b\d{12}\b',
        '[AADHAAR]',
        redacted
    )

    # Credit Card (16 digits)
    redacted = re.sub(
        r'\b\d{16}\b',
        '[CREDIT_CARD]',
        redacted
    )

    return {
        "original": text,
        "redacted": redacted
    }