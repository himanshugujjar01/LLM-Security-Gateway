from fastapi import APIRouter, Header
from app.auth.rbac import (
    get_rbac_policy,
    get_available_models,
    check_model_access
)

router = APIRouter()


@router.get("/rbac-policy")
def rbac_policy():
    return get_rbac_policy()


@router.get("/available-models")
def available_models(x_api_key: str = Header(None)):
    return get_available_models(x_api_key)


@router.get("/check-model-access")
def check_access(
    model_name: str,
    x_api_key: str = Header(None)
):
    return check_model_access(
        api_key=x_api_key,
        requested_model=model_name
    )