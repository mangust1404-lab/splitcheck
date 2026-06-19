from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Group, GroupMember, User
from app.schemas.group import (
    GroupCreate,
    GroupOut,
    GroupUpdate,
    JoinRequest,
    MemberCreate,
    MemberOut,
)

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.get("", response_model=list[GroupOut])
async def list_groups(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .where(GroupMember.user_id == user.id)
        .options(selectinload(Group.members))
        .distinct()
    )
    return result.scalars().all()


@router.post("", response_model=GroupOut, status_code=201)
async def create_group(
    body: GroupCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = Group(
        name=body.name,
        base_currency=body.base_currency,
        created_by_id=user.id,
    )
    db.add(group)
    await db.flush()

    member = GroupMember(
        group_id=group.id,
        user_id=user.id,
        display_name=user.display_name,
        role="admin",
    )
    db.add(member)
    await db.commit()

    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.members))
    )
    return result.scalar_one()


@router.get("/{group_id}", response_model=GroupOut)
async def get_group(
    group_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = await _get_group_for_user(group_id, user.id, db)
    return group


@router.patch("/{group_id}", response_model=GroupOut)
async def update_group(
    group_id: int,
    body: GroupUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = await _get_group_for_user(group_id, user.id, db)

    if body.name is not None:
        group.name = body.name
    if body.base_currency is not None:
        group.base_currency = body.base_currency
    if body.status is not None:
        group.status = body.status
        if body.status == "archived":
            group.archived_at = datetime.now(timezone.utc)
        elif body.status == "active":
            group.archived_at = None

    await db.commit()
    await db.refresh(group)
    return group


@router.post("/{group_id}/join", response_model=MemberOut)
async def join_group(
    group_id: int,
    body: JoinRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Group).where(Group.id == group_id, Group.invite_code == body.invite_code)
    )
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    # Check if already a member
    existing = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.user_id == user.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already a member")

    # Link to existing virtual member or create new
    if body.link_to_member_id:
        result = await db.execute(
            select(GroupMember).where(
                GroupMember.id == body.link_to_member_id,
                GroupMember.group_id == group_id,
                GroupMember.user_id.is_(None),
            )
        )
        member = result.scalar_one_or_none()
        if member is None:
            raise HTTPException(status_code=404, detail="Virtual member not found")
        member.user_id = user.id
    else:
        member = GroupMember(
            group_id=group_id,
            user_id=user.id,
            display_name=user.display_name,
            role="member",
        )
        db.add(member)

    await db.commit()
    await db.refresh(member)
    return member


@router.post("/{group_id}/members", response_model=MemberOut, status_code=201)
async def add_virtual_member(
    group_id: int,
    body: MemberCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_group_for_user(group_id, user.id, db)

    member = GroupMember(
        group_id=group_id,
        display_name=body.display_name,
        role="member",
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def _get_group_for_user(
    group_id: int, user_id: int, db: AsyncSession
) -> Group:
    result = await db.execute(
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .where(Group.id == group_id, GroupMember.user_id == user_id)
        .options(selectinload(Group.members))
    )
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group
