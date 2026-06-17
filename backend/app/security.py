import hmac
from fastapi import Header, HTTPException, status
from .config import settings


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    """Constant-time API key check. Auth disabled when API_KEY is empty."""
    expected = settings.api_key
    if not expected:
        return  # auth disabled
    if not x_api_key or not hmac.compare_digest(x_api_key.encode(), expected.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing X-API-Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
