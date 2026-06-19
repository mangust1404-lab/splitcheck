from pydantic import BaseModel


class AuthRequest(BaseModel):
    init_data: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    display_name: str


class UserOut(BaseModel):
    id: int
    telegram_id: int
    display_name: str
    avatar_url: str | None

    model_config = {"from_attributes": True}
