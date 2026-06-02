from typing import Optional
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

_bearer = HTTPBearer(auto_error=False)


async def require_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
):
    """Protect every route with a static API key.

    Skip auth entirely when API_KEY is not configured (local dev convenience).
    """
    if not settings.api_key:
        return  # auth disabled — local dev mode

    if credentials is None or credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Pass it as: Authorization: Bearer <key>",
            headers={"WWW-Authenticate": "Bearer"},
        )
