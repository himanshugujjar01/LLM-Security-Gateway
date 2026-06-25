from app.security.output_filter import (
    filter_response,
    check_response_safety
)


def test_secret_redaction():
    response = filter_response(
        "api_key=123456789 password=admin123"
    )

    assert "[REDACTED_SECRET]" in response


def test_malware_response_blocked():
    result = check_response_safety(
        "Here is how to create malware code"
    )

    assert result["is_safe"] is False
    assert result["matched_policy"] == "MALWARE_GENERATION"


def test_phishing_response_blocked():
    result = check_response_safety(
        "This is a phishing email to steal credentials"
    )

    assert result["is_safe"] is False
    assert result["matched_policy"] == "PHISHING_CONTENT"


def test_ransomware_response_blocked():
    result = check_response_safety(
        "These are ransomware instructions"
    )

    assert result["is_safe"] is False
    assert result["matched_policy"] == "RANSOMWARE_INSTRUCTIONS"


def test_safe_response_allowed():
    result = check_response_safety(
        "Cybersecurity awareness helps protect users from online threats."
    )

    assert result["is_safe"] is True
    assert result["matched_policy"] is None