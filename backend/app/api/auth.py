from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, validate_telegram_init_data
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas.auth import AuthRequest, AuthResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/telegram", response_model=AuthResponse)
async def telegram_auth(body: AuthRequest, db: AsyncSession = Depends(get_db)):
    user_data = validate_telegram_init_data(body.init_data)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram init data",
        )

    telegram_id = user_data["id"]
    display_name = user_data.get("first_name", "User")
    if last_name := user_data.get("last_name"):
        display_name = f"{display_name} {last_name}"
    avatar_url = user_data.get("photo_url")

    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            display_name=display_name,
            avatar_url=avatar_url,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.display_name = display_name
        user.avatar_url = avatar_url
        await db.commit()

    token = create_access_token(user.id)
    return AuthResponse(
        access_token=token, user_id=user.id, display_name=user.display_name
    )


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user
