"""Security middleware for HOME-AI-AUTOMATION."""

from flask import Flask, Response


def add_security_headers(app: Flask) -> None:
    """Add security headers to all responses."""

    @app.after_request
    def set_security_headers(response: Response) -> Response:
        """Set security headers on response."""
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Strict transport security (HTTPS)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' data:;"
        )

        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions policy
        response.headers['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )

        return response


def setup_rate_limiting(app: Flask) -> None:
    """Setup rate limiting for API endpoints."""
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    # Store limiter for use in routes
    app.limiter = limiter

    return limiter


def sanitize_log_data(data: str) -> str:
    """Sanitize log data to remove sensitive information."""
    import re

    # Remove potential API keys
    data = re.sub(r'(api[_-]?key|token|password|secret)[\s:=]+[\w-]+',
                  r'\1=***REDACTED***', data, flags=re.IGNORECASE)

    # Remove bearer tokens
    data = re.sub(r'Bearer\s+[\w-]+', 'Bearer ***REDACTED***', data, flags=re.IGNORECASE)

    # Remove OpenAI API keys (sk-...)
    data = re.sub(r'sk-[a-zA-Z0-9]{48}', 'sk-***REDACTED***', data)

    return data
