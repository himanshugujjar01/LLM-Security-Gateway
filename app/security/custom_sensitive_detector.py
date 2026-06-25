import re


CUSTOM_PATTERNS = {
    "INTERNAL_PROJECT_CODE": [
        r"\bPROJECT-[A-Z0-9-]{3,30}\b",
        r"\bPROJ-[A-Z0-9-]{3,30}\b",
        r"\bINT-[A-Z0-9-]{3,30}\b",
        r"\bCONFIDENTIAL-[A-Z0-9-]{3,30}\b",
        r"\bCLIENT-[A-Z0-9-]{3,30}\b",
        r"\b[A-Z]{2,5}-SEC-\d{3,6}\b",
        r"\b[A-Z]{2,5}-PROJ-\d{3,6}\b"
    ],

    "SSN": [
        r"\b\d{3}-\d{2}-\d{4}\b"
    ],

    "PHI": [
        r"\bMRN[:\s-]*[A-Z0-9-]{4,20}\b",
        r"\bMedical Record Number[:\s-]*[A-Z0-9-]{4,20}\b",
        r"\bPatient ID[:\s-]*[A-Z0-9-]{4,20}\b",
        r"\bHospital ID[:\s-]*[A-Z0-9-]{4,20}\b",
        r"\bHealth ID[:\s-]*[A-Z0-9-]{4,20}\b",
        r"\bInsurance ID[:\s-]*[A-Z0-9-]{4,20}\b",
        r"\bHealth Insurance Number[:\s-]*[A-Z0-9-]{4,20}\b",
        r"\bdiagnosed with [A-Za-z ]{3,40}\b",
        r"\btreatment for [A-Za-z ]{3,40}\b"
    ]
}


def detect_custom_sensitive_data(text: str):
    redacted_text = text
    entities_found = []

    for entity_type, patterns in CUSTOM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, redacted_text, flags=re.IGNORECASE):
                entities_found.append(entity_type)

                redacted_text = re.sub(
                    pattern,
                    f"<{entity_type}>",
                    redacted_text,
                    flags=re.IGNORECASE
                )

    return {
        "original": text,
        "redacted": redacted_text,
        "entities_found": list(set(entities_found))
    }