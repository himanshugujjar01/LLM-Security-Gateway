import re

import re

def filter_response(response):
    if isinstance(response, dict):
        response = str(response)

    patterns = [
        r"api[_-]?key",
        r"password",
        r"secret"
    ]

    for pattern in patterns:
        response = re.sub(
            pattern,
            "[REDACTED]",
            response,
            flags=re.IGNORECASE
        )

    return response
  