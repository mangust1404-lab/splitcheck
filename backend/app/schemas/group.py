from datetime import datetime

from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    base_currency: str = "KZT"


class GroupUpdate(BaseModel):
    name: str | None = None
    base_currency: str | None = None
    status: str | None = None  # "active" or "archived"


class MemberCreate(BaseModel):
    display_name: str


class MemberOut(BaseModel):
    id: int
    display_name: str
    user_id: int | None
    role: str

    model_config = {"from_attributes": True}


class GroupOut(BaseModel):
    id: int
    name: str
    base_currency: str
    invite_code: str
    status: str
    created_at: datetime
    archived_at: datetime | None
    members: list[MemberOut] = []

    model_config = {"from_attributes": True}


class GroupInvitePreview(BaseModel):
    id: int
    name: str
    base_currency: str
    members: list[MemberOut] = []

    model_config = {"from_attributes": True}


class JoinRequest(BaseModel):
    invite_code: str
    link_to_member_id: int | None = None  # optional: link to existing virtual member
