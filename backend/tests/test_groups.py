import pytest
import pytest_asyncio

from app.auth import create_access_token
from app.models import User


@pytest_asyncio.fixture
async def auth_headers(db):
    user = User(telegram_id=11111, display_name="TestUser")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def second_user_headers(db):
    user = User(telegram_id=22222, display_name="SecondUser")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
class TestGroups:
    async def test_create_group(self, client, auth_headers):
        resp = await client.post(
            "/api/groups",
            json={"name": "Trip to Bali", "base_currency": "USD"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Trip to Bali"
        assert data["base_currency"] == "USD"
        assert len(data["members"]) == 1
        assert data["members"][0]["role"] == "admin"

    async def test_list_groups(self, client, auth_headers):
        await client.post(
            "/api/groups",
            json={"name": "Trip 1"},
            headers=auth_headers,
        )
        resp = await client.get("/api/groups", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_add_virtual_member(self, client, auth_headers):
        resp = await client.post(
            "/api/groups", json={"name": "Test"}, headers=auth_headers
        )
        group_id = resp.json()["id"]

        resp = await client.post(
            f"/api/groups/{group_id}/members",
            json={"display_name": "Virtual Bob"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["display_name"] == "Virtual Bob"
        assert resp.json()["user_id"] is None

    async def test_join_group(self, client, auth_headers, second_user_headers):
        resp = await client.post(
            "/api/groups", json={"name": "Join Test"}, headers=auth_headers
        )
        group = resp.json()

        resp = await client.post(
            f"/api/groups/{group['id']}/join",
            json={"invite_code": group["invite_code"]},
            headers=second_user_headers,
        )
        assert resp.status_code == 200

    async def test_archive_group(self, client, auth_headers):
        resp = await client.post(
            "/api/groups", json={"name": "Archive Me"}, headers=auth_headers
        )
        group_id = resp.json()["id"]

        resp = await client.patch(
            f"/api/groups/{group_id}",
            json={"status": "archived"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "archived"
        assert resp.json()["archived_at"] is not None
