from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import time

request_log = {}

class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host

        current_time = time.time()

        if ip not in request_log:
            request_log[ip] = []

        request_log[ip] = [
            t for t in request_log[ip]
            if current_time - t < 60
        ]

        if len(request_log[ip]) >= 5:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded. Try again later."
                }
            )

        request_log[ip].append(current_time)

        response = await call_next(request)
        return response