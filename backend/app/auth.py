import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs

from jose import jwt

from app.config import settings


def validate_telegram_init_data(init_data: str) -> dict | None:
    """Validate Telegram WebApp initData and return parsed user data.
    Returns None if validation fails.
    """
    parsed = parse_qs(init_data)
    if "hash" not in parsed:
        return None

    received_hash = parsed.pop("hash")[0]

    data_check_parts = []
    for key in sorted(parsed.keys()):
        data_check_parts.append(f"{key}={parsed[key][0]}")
    data_check_string = "\n".join(data_check_parts)

    secret_key = hmac.new(
        b"WebAppData", settings.bot_token.encode(), hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    if "user" not in parsed:
        return None

    return json.loads(parsed["user"][0])


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return int(payload["sub"])
    except (jwt.JWTError, KeyError, ValueError):
        return None
