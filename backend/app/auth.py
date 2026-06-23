import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl

from jose import jwt

from app.config import settings

logger = logging.getLogger(__name__)


def validate_telegram_init_data(init_data: str) -> dict | None:
    """Validate Telegram WebApp initData and return parsed user data.
    Returns None if validation fails.
    """
    # Use parse_qsl (treats + as space, consistent with Telegram's urlSafeDecode)
    pairs = parse_qsl(init_data, keep_blank_values=True)
    data = dict(pairs)

    if "hash" not in data:
        logger.warning("No hash in initData")
        return None

    received_hash = data.pop("hash")
    # For HMAC validation: only 'hash' is excluded from data_check_string
    # 'signature' is INCLUDED (it's excluded only for Ed25519 third-party validation)

    # Build data-check-string: sorted key=value pairs joined by \n
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )

    secret_key = hmac.new(
        b"WebAppData", settings.bot_token.encode(), hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        logger.warning("Telegram auth HMAC mismatch")
        return None

    if "user" not in data:
        logger.warning("No user field in initData")
        return None

    return json.loads(data["user"])


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
