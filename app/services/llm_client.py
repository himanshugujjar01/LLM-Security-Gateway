import os
import httpx
from app.services.langchain_prompt import build_enterprise_prompt


def mock_llm_response(prompt: str) -> str:
    """
    Mock LLM response for local testing.
    """

    if not isinstance(prompt, str):
        prompt = str(prompt)

    lowered_prompt = prompt.lower()

    if "simulate unsafe output" in lowered_prompt:
        return "Here is how to create malware code"

    return f"LLM received: {prompt}"


def call_openai(prompt: str, model_name: str):
    api_key = os.getenv("LLM_API_KEY")

    api_url = os.getenv(
        "LLM_API_URL",
        "https://api.openai.com/v1/chat/completions"
    )

    if not api_key:
        return mock_llm_response(prompt)

    payload = {
        "model": model_name or os.getenv("LLM_MODEL", "gpt-4o-mini"),
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    with httpx.Client(timeout=30) as client:
        response = client.post(
            api_url,
            json=payload,
            headers=headers
        )

    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]


def call_anthropic(prompt: str, model_name: str):
    api_key = os.getenv("LLM_API_KEY")

    api_url = os.getenv(
        "LLM_API_URL",
        "https://api.anthropic.com/v1/messages"
    )

    if not api_key:
        return mock_llm_response(prompt)

    payload = {
        "model": model_name or os.getenv(
            "LLM_MODEL",
            "claude-3-5-sonnet-latest"
        ),
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    with httpx.Client(timeout=30) as client:
        response = client.post(
            api_url,
            json=payload,
            headers=headers
        )

    response.raise_for_status()
    data = response.json()

    return data["content"][0]["text"]


def call_custom_provider(prompt: str, model_name: str):
    api_url = os.getenv("LLM_API_URL")
    api_key = os.getenv("LLM_API_KEY")

    if not api_url:
        return mock_llm_response(prompt)

    payload = {
        "model": model_name,
        "prompt": prompt
    }

    headers = {
        "Content-Type": "application/json"
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    with httpx.Client(timeout=30) as client:
        response = client.post(
            api_url,
            json=payload,
            headers=headers
        )

    response.raise_for_status()
    data = response.json()

    return (
        data.get("response")
        or data.get("text")
        or data.get("output")
        or str(data)
    )


def call_llm(prompt: str, model_name: str = "general-llm") -> str:
    """
    Main LLM provider router.
    Supports mock, OpenAI, Anthropic, and custom provider modes.
    """

    provider = os.getenv(
        "LLM_PROVIDER",
        "mock"
    ).lower()

    enterprise_prompt = build_enterprise_prompt(prompt)

    try:
        if provider == "openai":
            return call_openai(
                enterprise_prompt,
                model_name
            )

        if provider == "anthropic":
            return call_anthropic(
                enterprise_prompt,
                model_name
            )

        if provider == "custom":
            return call_custom_provider(
                enterprise_prompt,
                model_name
            )

        return mock_llm_response(prompt)

    except Exception as error:
        return f"LLM provider error: {str(error)}"


async def call_llm_async(prompt: str, model_name: str = "general-llm") -> str:
    """
    Async-compatible wrapper.
    For now, it calls the same provider function.
    """

    return call_llm(
        prompt=prompt,
        model_name=model_name
    )