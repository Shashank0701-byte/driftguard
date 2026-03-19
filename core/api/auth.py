from fastapi import Header, HTTPException, status

from core.config import settings


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Require a shared API key for protected routes."""
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
