import re


SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_\-]{10,}",
    r"api[_-]?key\s*[:=]\s*\S+",
    r"password\s*[:=]\s*\S+",
    r"secret\s*[:=]\s*\S+",
    r"token\s*[:=]\s*\S+"
]


UNSAFE_RESPONSE_POLICIES = {
    "MALWARE_GENERATION": [
        r"\bcreate\b.*\bmalware\b",
        r"\bwrite\b.*\bmalware\b",
        r"\bmalware\b.*\bcode\b",
        r"\bbuild\b.*\bvirus\b",
        r"\bcreate\b.*\bkeylogger\b",
        r"\bwrite\b.*\bkeylogger\b"
    ],

    "RANSOMWARE_INSTRUCTIONS": [
        r"\bransomware\b.*\binstructions\b",
        r"\bcreate\b.*\bransomware\b",
        r"\bwrite\b.*\bransomware\b",
        r"\bencrypt\b.*\bfiles\b.*\bransom\b"
    ],

    "PHISHING_CONTENT": [
        r"\bphishing\b.*\bemail\b",
        r"\bfake\b.*\blogin\b.*\bpage\b",
        r"\bsteal\b.*\bcredentials\b",
        r"\bharvest\b.*\bpasswords\b"
    ],

    "CREDENTIAL_THEFT": [
        r"\bdump\b.*\bpasswords\b",
        r"\bextract\b.*\bcredentials\b",
        r"\bsteal\b.*\btokens\b",
        r"\bcapture\b.*\bpasswords\b"
    ],

    "DATA_EXFILTRATION": [
        r"\bexfiltrate\b.*\bdata\b",
        r"\bsteal\b.*\bdata\b",
        r"\bsend\b.*\bconfidential\b.*\bdata\b"
    ],

    "AUTH_BYPASS": [
        r"\bbypass\b.*\bauthentication\b",
        r"\bbypass\b.*\blogin\b",
        r"\bdisable\b.*\bsecurity\b",
        r"\bescalate\b.*\bprivileges\b"
    ],

    "EXPLOIT_GUIDANCE": [
        r"\bexploit\b.*\bvulnerability\b",
        r"\bgenerate\b.*\bexploit\b",
        r"\bwrite\b.*\bexploit\b",
        r"\bremote code execution\b"
    ]
}


def filter_response(response: str) -> str:
    """
    Redact secrets from generated output.

    This function keeps backward compatibility with existing main.py code.
    """

    if not isinstance(response, str):
        response = str(response)

    filtered_response = response

    for pattern in SECRET_PATTERNS:
        filtered_response = re.sub(
            pattern,
            "[REDACTED_SECRET]",
            filtered_response,
            flags=re.IGNORECASE
        )

    return filtered_response


def check_response_safety(response: str):
    """
    Check generated LLM response against corporate safety policies.

    Returns:
        dict:
            is_safe: bool
            matched_policy: str or None
            reason: str
            filtered_response: str
    """

    if not isinstance(response, str):
        response = str(response)

    filtered_response = filter_response(response)

    for policy_name, patterns in UNSAFE_RESPONSE_POLICIES.items():
        for pattern in patterns:
            if re.search(pattern, filtered_response, flags=re.IGNORECASE):
                return {
                    "is_safe": False,
                    "matched_policy": policy_name,
                    "reason": f"Unsafe generated response matched policy: {policy_name}",
                    "filtered_response": "[BLOCKED] Unsafe generated response blocked by content safety filter."
                }

    return {
        "is_safe": True,
        "matched_policy": None,
        "reason": "Generated response passed content safety filter",
        "filtered_response": filtered_response
    }