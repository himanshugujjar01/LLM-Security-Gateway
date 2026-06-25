from app.security.custom_sensitive_detector import detect_custom_sensitive_data


def test_internal_project_code_redaction():
    result = detect_custom_sensitive_data(
        "This belongs to PROJECT-ALPHA-2026"
    )

    assert "<INTERNAL_PROJECT_CODE>" in result["redacted"]
    assert "INTERNAL_PROJECT_CODE" in result["entities_found"]


def test_ssn_redaction():
    result = detect_custom_sensitive_data(
        "Employee SSN is 123-45-6789"
    )

    assert "<SSN>" in result["redacted"]
    assert "SSN" in result["entities_found"]


def test_phi_patient_id_redaction():
    result = detect_custom_sensitive_data(
        "Patient ID: HOSP-7788"
    )

    assert "<PHI>" in result["redacted"]
    assert "PHI" in result["entities_found"]


def test_phi_medical_condition_redaction():
    result = detect_custom_sensitive_data(
        "Patient diagnosed with fever"
    )

    assert "<PHI>" in result["redacted"]
    assert "PHI" in result["entities_found"]