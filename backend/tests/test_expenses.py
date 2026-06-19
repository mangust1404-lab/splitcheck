import pytest
import pytest_asyncio
from decimal import Decimal

from app.auth import create_access_token
from app.models import User, Group, GroupMember


@pytest_asyncio.fixture
async def group_setup(db):
    """Create user, group, and 3 members. Return dict with ids and auth headers."""
    user = User(telegram_id=33333, display_name="Payer")
    db.add(user)
    await db.flush()

    group = Group(name="Test Trip", base_currency="KZT", created_by_id=user.id)
    db.add(group)
    await db.flush()

    m1 = GroupMember(group_id=group.id, user_id=user.id, display_name="Payer", role="admin")
    m2 = GroupMember(group_id=group.id, display_name="Alice")
    m3 = GroupMember(group_id=group.id, display_name="Bob")
    db.add_all([m1, m2, m3])
    await db.commit()

    for m in [m1, m2, m3]:
        await db.refresh(m)

    token = create_access_token(user.id)
    return {
        "group_id": group.id,
        "member_ids": [m1.id, m2.id, m3.id],
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.mark.asyncio
class TestExpenses:
    async def test_create_equal_expense(self, client, group_setup):
        s = group_setup
        resp = await client.post(
            f"/api/groups/{s['group_id']}/expenses",
            json={
                "title": "Dinner",
                "total_amount": "9000",
                "currency": "KZT",
                "paid_by_id": s["member_ids"][0],
                "split_type": "equal",
                "split_among": s["member_ids"],
            },
            headers=s["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Dinner"
        assert len(data["shares"]) == 3
        assert Decimal(data["shares"][0]["amount"]) == Decimal("3000.00")

    async def test_create_custom_expense(self, client, group_setup):
        s = group_setup
        resp = await client.post(
            f"/api/groups/{s['group_id']}/expenses",
            json={
                "title": "Taxi",
                "total_amount": "5000",
                "currency": "KZT",
                "paid_by_id": s["member_ids"][0],
                "split_type": "custom",
                "shares": [
                    {"member_id": s["member_ids"][1], "amount": "3000"},
                    {"member_id": s["member_ids"][2], "amount": "2000"},
                ],
            },
            headers=s["headers"],
        )
        assert resp.status_code == 201
        assert len(resp.json()["shares"]) == 2

    async def test_list_expenses(self, client, group_setup):
        s = group_setup
        await client.post(
            f"/api/groups/{s['group_id']}/expenses",
            json={
                "title": "Lunch",
                "total_amount": "3000",
                "currency": "KZT",
                "paid_by_id": s["member_ids"][0],
                "split_type": "equal",
                "split_among": s["member_ids"],
            },
            headers=s["headers"],
        )
        resp = await client.get(
            f"/api/groups/{s['group_id']}/expenses", headers=s["headers"]
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_delete_expense(self, client, group_setup):
        s = group_setup
        resp = await client.post(
            f"/api/groups/{s['group_id']}/expenses",
            json={
                "title": "To Delete",
                "total_amount": "1000",
                "currency": "KZT",
                "paid_by_id": s["member_ids"][0],
                "split_type": "equal",
                "split_among": s["member_ids"],
            },
            headers=s["headers"],
        )
        expense_id = resp.json()["id"]

        resp = await client.delete(
            f"/api/expenses/{expense_id}", headers=s["headers"]
        )
        assert resp.status_code == 204
