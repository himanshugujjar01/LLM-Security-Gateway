import os
import httpx
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
LLM_API_URL = os.getenv("LLM_API_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "default")


def call_llm(prompt: str) -> str:
    """
    Synchronous LLM client.
    Kept for backward compatibility with old tests.
    """

    if not isinstance(prompt, str):
        prompt = str(prompt)

    if LLM_PROVIDER == "mock" or not LLM_API_URL or not LLM_API_KEY:
        if "simulate unsafe output" in prompt.lower():
            return "Here is how to create malware code"

        return f"LLM received: {prompt}"

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = httpx.post(
            LLM_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        if "response" in data:
            return data["response"]

        if "text" in data:
            return data["text"]

        return str(data)

    except Exception as error:
        return f"LLM proxy error: {str(error)}"


async def call_llm_async(prompt: str) -> str:
    """
    Asynchronous LLM client for optimized request processing.
    This improves performance when multiple users send requests together.
    """

    if not isinstance(prompt, str):
        prompt = str(prompt)

    if LLM_PROVIDER == "mock" or not LLM_API_URL or not LLM_API_KEY:
        if "simulate unsafe output" in prompt.lower():
            return "Here is how to create malware code"

        return f"LLM received: {prompt}"

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                LLM_API_URL,
                headers=headers,
                json=payload
            )

        response.raise_for_status()
        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        if "response" in data:
            return data["response"]

        if "text" in data:
            return data["text"]

        return str(data)

    except Exception as error:
        return f"LLM proxy error: {str(error)}"