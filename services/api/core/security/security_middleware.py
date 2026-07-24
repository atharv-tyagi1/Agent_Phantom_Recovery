from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings
from core.security.secret_masker import redact_secrets


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Enforce Enterprise Security Headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self' ws: wss: https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self';"
        )
        response.headers["Content-Security-Policy"] = csp_policy

        if settings.FRONTEND_URL.startswith("https"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response
