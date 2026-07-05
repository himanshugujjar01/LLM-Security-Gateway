import os
import json
import hashlib
from difflib import SequenceMatcher

try:
    import redis
except Exception:
    redis = None


CACHE_INDEX_KEY = "llm_semantic_cache:index"


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)

    return " ".join(
        text.lower().strip().split()
    )


def similarity_score(text_a: str, text_b: str) -> float:
    return SequenceMatcher(
        None,
        normalize_text(text_a),
        normalize_text(text_b)
    ).ratio()


def get_redis_client():
    if redis is None:
        return None

    try:
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))

        client = redis.Redis(
            host=host,
            port=port,
            decode_responses=True
        )

        client.ping()
        return client

    except Exception:
        return None


def cache_enabled() -> bool:
    return os.getenv(
        "SEMANTIC_CACHE_ENABLED",
        "true"
    ).lower() == "true"


def make_cache_key(model_name: str, prompt: str) -> str:
    raw_key = f"{model_name}:{normalize_text(prompt)}"

    digest = hashlib.sha256(
        raw_key.encode()
    ).hexdigest()

    return f"llm_semantic_cache:{digest}"


def get_cached_response(prompt: str, model_name: str = "general-llm"):
    """
    Checks Redis for exact or semantically similar cached response.
    """

    if not cache_enabled():
        return None

    client = get_redis_client()

    if client is None:
        return None

    try:
        threshold = float(
            os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.88")
        )

        exact_key = make_cache_key(
            model_name,
            prompt
        )

        exact_value = client.get(exact_key)

        if exact_value:
            data = json.loads(exact_value)
            data["cache_type"] = "exact"
            return data

        cached_keys = client.smembers(CACHE_INDEX_KEY)

        for key in cached_keys:
            cached_value = client.get(key)

            if not cached_value:
                continue

            data = json.loads(cached_value)

            if data.get("model_name") != model_name:
                continue

            score = similarity_score(
                prompt,
                data.get("prompt", "")
            )

            if score >= threshold:
                data["cache_type"] = "semantic"
                data["similarity_score"] = round(score, 2)
                return data

    except Exception:
        return None

    return None


def set_cached_response(
    prompt: str,
    response: str,
    model_name: str = "general-llm"
):
    """
    Stores safe LLM response in Redis cache.
    """

    if not cache_enabled():
        return False

    client = get_redis_client()

    if client is None:
        return False

    try:
        cache_key = make_cache_key(
            model_name,
            prompt
        )

        data = {
            "prompt": prompt,
            "response": response,
            "model_name": model_name
        }

        client.set(
            cache_key,
            json.dumps(data),
            ex=3600
        )

        client.sadd(
            CACHE_INDEX_KEY,
            cache_key
        )

        return True

    except Exception:
        return False