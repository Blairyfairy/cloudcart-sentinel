from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.db.session import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def require_user(
    token: Annotated[str, Depends(oauth2_scheme)], settings: SettingsDep
) -> str:
    subject = decode_access_token(token, settings)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return subject

CurrentUser = Annotated[str, Depends(require_user)]
