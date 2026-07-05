import re


PHI_KEYWORDS = [
    "patient",
    "diagnosis",
    "medical record",
    "medical history",
    "prescription",
    "blood pressure",
    "diabetes",
    "cancer",
    "hiv",
    "asthma",
    "medicine",
    "hospital",
    "doctor",
    "treatment",
    "surgery",
    "lab report",
    "insurance id",
    "health id"
]


PHI_REGEX_PATTERNS = {
    "MEDICAL_RECORD_NUMBER": r"\b(MRN|medical record number)\s*[:\-]?\s*[A-Za-z0-9\-]{4,20}\b",
    "PATIENT_ID": r"\b(patient id|PID)\s*[:\-]?\s*[A-Za-z0-9\-]{4,20}\b",
    "HEALTH_INSURANCE_ID": r"\b(health insurance id|insurance id)\s*[:\-]?\s*[A-Za-z0-9\-]{4,25}\b",
    "HOSPITAL_ID": r"\b(hospital id)\s*[:\-]?\s*[A-Za-z0-9\-]{4,25}\b"
}


def detect_phi(text: str):
    """
    Detects Protected Health Information style content.
    """

    if not isinstance(text, str):
        text = str(text)

    detected_items = []
    lowered_text = text.lower()

    for keyword in PHI_KEYWORDS:
        if keyword in lowered_text:
            detected_items.append(
                {
                    "type": "PHI_KEYWORD",
                    "value": keyword
                }
            )

    for entity_type, pattern in PHI_REGEX_PATTERNS.items():
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        for match in matches:
            detected_items.append(
                {
                    "type": entity_type,
                    "value": str(match)
                }
            )

    return {
        "phi_detected": len(detected_items) > 0,
        "detected_items": detected_items
    }


def redact_phi(text: str):
    """
    Redacts PHI-related sensitive information.
    """

    if not isinstance(text, str):
        text = str(text)

    redacted_text = text

    for entity_type, pattern in PHI_REGEX_PATTERNS.items():
        redacted_text = re.sub(
            pattern,
            f"[{entity_type}]",
            redacted_text,
            flags=re.IGNORECASE
        )

    for keyword in PHI_KEYWORDS:
        redacted_text = re.sub(
            rf"\b{re.escape(keyword)}\b",
            "[PHI]",
            redacted_text,
            flags=re.IGNORECASE
        )

    return redacted_text