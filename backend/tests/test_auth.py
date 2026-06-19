import hashlib
import hmac
import json
from urllib.parse import urlencode

import pytest
from app.auth import create_access_token, decode_access_token, validate_telegram_init_data
from app.config import settings


def make_init_data(user_data: dict, bot_token: str = "") -> str:
    token = bot_token or settings.bot_token
    params = {
        "user": json.dumps(user_data),
        "auth_date": "1700000000",
    }
    data_check_string = "\n".join(
        f"{k}={params[k]}" for k in sorted(params.keys())
    )
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    hash_value = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()
    params["hash"] = hash_value
    return urlencode(params, doseq=True)


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token(42)
        user_id = decode_access_token(token)
        assert user_id == 42

    def test_decode_invalid_token(self):
        assert decode_access_token("garbage") is None


class TestTelegramValidation:
    def test_valid_init_data(self):
        settings.bot_token = "123456:ABC-TEST"
        user = {"id": 999, "first_name": "Test", "last_name": "User"}
        init_data = make_init_data(user)
        result = validate_telegram_init_data(init_data)
        assert result is not None
        assert result["id"] == 999

    def test_invalid_hash(self):
        settings.bot_token = "123456:ABC-TEST"
        result = validate_telegram_init_data("user=%7B%7D&auth_date=1&hash=bad")
        assert result is None


@pytest.mark.asyncio
class TestAuthEndpoint:
    async def test_telegram_auth_creates_user(self, client):
        settings.bot_token = "123456:ABC-TEST"
        user = {"id": 12345, "first_name": "Alex", "last_name": "L"}
        init_data = make_init_data(user)

        resp = await client.post("/api/auth/telegram", json={"init_data": init_data})
        assert resp.status_code == 200
        data = resp.json()
        assert data["display_name"] == "Alex L"
        assert "access_token" in data

    async def test_telegram_auth_invalid(self, client):
        resp = await client.post(
            "/api/auth/telegram", json={"init_data": "hash=invalid"}
        )
        assert resp.status_code == 401
