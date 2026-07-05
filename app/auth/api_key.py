from fastapi import HTTPException
from app.auth.rbac import API_KEY_USER_MAP


def verify_api_key(api_key: str):
    """
    Verifies whether the provided API key is valid.

    Now it supports all RBAC API keys:
    - my-secret-key
    - hr-secret-key
    - finance-secret-key
    - security-secret-key
    """

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key missing"
        )

    if api_key not in API_KEY_USER_MAP:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return True