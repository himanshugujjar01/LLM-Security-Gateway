from app.auth.rbac import check_model_access, get_available_models


def test_admin_can_access_finance_model():
    result = check_model_access(
        api_key="my-secret-key",
        requested_model="finance-llm"
    )

    assert result["allowed"] is True


def test_hr_can_access_hr_model():
    result = check_model_access(
        api_key="hr-secret-key",
        requested_model="hr-llm"
    )

    assert result["allowed"] is True


def test_hr_cannot_access_finance_model():
    result = check_model_access(
        api_key="hr-secret-key",
        requested_model="finance-llm"
    )

    assert result["allowed"] is False


def test_invalid_api_key_has_no_models():
    result = get_available_models(
        api_key="wrong-key"
    )

    assert result["authorized"] is False
    assert result["available_models"] == []