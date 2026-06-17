import hmac
from fastapi import Header, HTTPException, status
from .config import settings


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    """Bearer-style API key check.

    If API_KEY is empty in the environment, auth is disabled (dev mode).
    Otherwise every request must send X-API-Key matching it, in constant time.
    """
    expected = settings.api_key
    if not expected:
        return
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing X-API-Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
