from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def create_access_token(subject: str, settings: Settings) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode(
        {"sub": subject, "exp": expires, "iat": datetime.now(UTC)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str, settings: Settings) -> str | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        return subject if isinstance(subject, str) else None
    except JWTError:
        return None
