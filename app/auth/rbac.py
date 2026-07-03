API_KEY_USER_MAP = {
    "my-secret-key": {
        "user_id": "admin_user",
        "department": "ADMIN",
        "role": "ADMIN"
    },

    "hr-secret-key": {
        "user_id": "hr_user",
        "department": "HR",
        "role": "USER"
    },

    "finance-secret-key": {
        "user_id": "finance_user",
        "department": "FINANCE",
        "role": "USER"
    },

    "security-secret-key": {
        "user_id": "security_user",
        "department": "SECURITY",
        "role": "ANALYST"
    }
}


MODEL_ACCESS_POLICY = {
    "ADMIN": [
        "general-llm",
        "hr-llm",
        "finance-llm",
        "security-llm"
    ],

    "HR": [
        "general-llm",
        "hr-llm"
    ],

    "FINANCE": [
        "general-llm",
        "finance-llm"
    ],

    "SECURITY": [
        "general-llm",
        "security-llm"
    ]
}


def get_user_context(api_key: str):
    """
    Returns user identity, department, and role based on API key.
    """

    return API_KEY_USER_MAP.get(api_key)


def get_available_models(api_key: str):
    """
    Returns AI models available for the user's department.
    """

    user_context = get_user_context(api_key)

    if not user_context:
        return {
            "authorized": False,
            "message": "Invalid API key",
            "available_models": []
        }

    department = user_context["department"]

    return {
        "authorized": True,
        "user_context": user_context,
        "available_models": MODEL_ACCESS_POLICY.get(department, [])
    }


def check_model_access(api_key: str, requested_model: str):
    """
    Checks whether a user is allowed to access the requested AI model.
    """

    user_context = get_user_context(api_key)

    if not user_context:
        return {
            "allowed": False,
            "reason": "Invalid API key",
            "user_context": None
        }

    department = user_context["department"]
    allowed_models = MODEL_ACCESS_POLICY.get(department, [])

    if requested_model in allowed_models:
        return {
            "allowed": True,
            "reason": "Model access allowed",
            "user_context": user_context,
            "allowed_models": allowed_models
        }

    return {
        "allowed": False,
        "reason": "Model access denied for this department",
        "user_context": user_context,
        "allowed_models": allowed_models
    }


def get_rbac_policy():
    """
    Returns complete RBAC policy for review/demo.
    """

    return {
        "rbac_status": "ENABLED",
        "policy_type": "Department-Based AI Model Access Control",
        "model_access_policy": MODEL_ACCESS_POLICY,
        "supported_departments": list(MODEL_ACCESS_POLICY.keys())
    }