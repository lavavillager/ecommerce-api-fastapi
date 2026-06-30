"""Хеширование паролей и работа с JWT-токенами."""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def _to_bytes(password: str) -> bytes:
    # bcrypt не поддерживает пароли длиннее 72 байт — безопасно усекаем.
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    """Возвращает bcrypt-хеш пароля."""
    return bcrypt.hashpw(_to_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля и хеша."""
    try:
        return bcrypt.checkpw(
            _to_bytes(plain_password), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(subject: str | int, expires_minutes: int | None = None) -> str:
    """Создаёт JWT access-токен для указанного субъекта (id пользователя)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Декодирует токен и возвращает subject (id) либо None при ошибке."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None
