from app.security.pii_detector import redact_pii

def test_email_redaction():
    result = redact_pii("My email is test@gmail.com")
    assert "[EMAIL]" in result["redacted"]

def test_phone_redaction():
    result = redact_pii("My phone is 9876543210")
    assert "[PHONE]" in result["redacted"]

def test_multiple_pii():
    result = redact_pii(
        "Email test@gmail.com Phone 9876543210 Credit Card 1234567812345678"
    )

    assert "[EMAIL]" in result["redacted"]
    assert "[PHONE]" in result["redacted"]
    assert "[CREDIT_CARD]" in result["redacted"]