# SplitCheck Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Telegram Mini App for splitting group expenses with LLM-powered receipt scanning.

**Architecture:** Monorepo with `backend/` (FastAPI + async SQLAlchemy + PostgreSQL) and `frontend/` (Vue 3 + Vite + Tailwind). Receipt OCR via Claude Vision API. Telegram Web App SDK for auth and notifications. Follows patterns from the existing almaty-guide project.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, Vue.js 3, Vite, Tailwind CSS, Pinia, Vue Router, Telegram Web App SDK, Anthropic Python SDK.

---

## File Structure

```
splitcheck/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    — FastAPI app, CORS, router includes
│   │   ├── config.py                  — pydantic-settings, env vars
│   │   ├── database.py                — async engine, session factory, get_db
│   │   ├── auth.py                    — Telegram initData validation, JWT encode/decode
│   │   ├── deps.py                    — FastAPI dependencies (get_current_user)
│   │   ├── models/
│   │   │   ├── __init__.py            — re-exports all models
│   │   │   ├── user.py                — User model
│   │   │   ├── group.py               — Group, GroupMember models
│   │   │   ├── expense.py             — Expense, ExpenseItem, ExpenseShare models
│   │   │   └── settlement.py          — Settlement model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                — AuthRequest, AuthResponse, UserOut
│   │   │   ├── group.py               — GroupCreate, GroupOut, MemberCreate, MemberOut
│   │   │   ├── expense.py             — ExpenseCreate, ExpenseOut, ItemOut, ShareOut
│   │   │   ├── receipt.py             — ReceiptScanResponse, ReceiptItem
│   │   │   └── settlement.py          — SettlementOut, SettlementUpdate, BalanceOut
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                — POST /api/auth/telegram
│   │   │   ├── groups.py              — CRUD /api/groups, /api/groups/:id/join, /members
│   │   │   ├── expenses.py            — CRUD /api/groups/:id/expenses, /api/expenses/:id
│   │   │   ├── receipts.py            — POST /api/receipts/scan
│   │   │   ├── settlements.py         — GET balances, GET/PATCH settlements
│   │   │   └── currencies.py          — GET /api/currencies/rates
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── receipt_scanner.py      — Claude Vision API integration
│   │       ├── settlement_calculator.py — balance calc + greedy minimization
│   │       └── currency.py             — exchange rate fetching + cache
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── alembic.ini
│   ├── tests/
│   │   ├── conftest.py                — test DB, fixtures, test client
│   │   ├── test_auth.py
│   │   ├── test_groups.py
│   │   ├── test_expenses.py
│   │   ├── test_settlement_calculator.py
│   │   └── test_receipts.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.js               — vue-router setup
│   │   ├── api/
│   │   │   ├── client.js              — axios instance with JWT interceptor
│   │   │   ├── auth.js                — login API call
│   │   │   ├── groups.js              — groups CRUD
│   │   │   ├── expenses.js            — expenses CRUD
│   │   │   ├── receipts.js            — receipt scan upload
│   │   │   └── settlements.js         — balances + settlements
│   │   ├── stores/
│   │   │   ├── auth.js                — Pinia store: user, token, login
│   │   │   └── groups.js              — Pinia store: groups list, current group
│   │   ├── composables/
│   │   │   ├── useTelegram.js         — Telegram WebApp SDK wrapper
│   │   │   └── useCurrency.js         — currency formatting
│   │   ├── components/
│   │   │   ├── GroupCard.vue           — trip card for list
│   │   │   ├── ExpenseItem.vue         — expense row in list
│   │   │   ├── ReceiptItemRow.vue      — single receipt item with assignment
│   │   │   ├── ParticipantPicker.vue   — popup with checkboxes for assigning
│   │   │   ├── ParticipantBar.vue      — avatar bar with brush mode
│   │   │   ├── BalanceBar.vue          — colored balance indicator
│   │   │   ├── SettlementCard.vue      — transfer card with actions
│   │   │   └── CurrencyInput.vue       — amount input with currency selector
│   │   ├── views/
│   │   │   ├── MyTrips.vue             — active/archived groups list
│   │   │   ├── CreateGroup.vue         — new trip form
│   │   │   ├── TripDetail.vue          — expenses/balances/settlements tabs
│   │   │   ├── AddExpense.vue          — manual expense entry
│   │   │   ├── ScanReceipt.vue         — camera + all-in-one assignment
│   │   │   └── GroupSettings.vue       — members, invite, archive
│   │   └── utils/
│   │       └── format.js              — currency/date formatting helpers
│   └── public/
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Phase 1: Backend Foundation

### Task 1: Backend Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/main.py`
- Create: `.gitignore`
- Create: `.env.example`

- [ ] **Step 1: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/

# Environment
.env

# Node
node_modules/
dist/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Superpowers
.superpowers/
```

- [ ] **Step 2: Create backend/requirements.txt**

```
fastapi==0.115.12
uvicorn[standard]==0.34.3
sqlalchemy[asyncio]==2.0.41
asyncpg==0.30.0
alembic==1.16.1
pydantic-settings==2.9.1
python-jose[cryptography]==3.4.0
python-multipart==0.0.20
httpx==0.28.1
anthropic==0.52.0
boto3==1.38.24
pytest==8.3.5
pytest-asyncio==0.26.0
httpx==0.28.1
```

- [ ] **Step 3: Create backend/.env.example**

```env
DATABASE_URL=postgresql+asyncpg://splitcheck:splitcheck_dev@localhost:5432/splitcheck
BOT_TOKEN=your-telegram-bot-token
JWT_SECRET=your-jwt-secret-change-me
ANTHROPIC_API_KEY=your-anthropic-api-key
CORS_ORIGINS=http://localhost:5173,https://web.telegram.org
R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET=splitcheck-receipts
```

- [ ] **Step 4: Create backend/app/__init__.py**

Empty file.

- [ ] **Step 5: Create backend/app/config.py**

```python
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://splitcheck:splitcheck_dev@localhost:5432/splitcheck"
    bot_token: str = ""
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 720  # 30 days
    cors_origins: str = "http://localhost:5173,https://web.telegram.org"
    anthropic_api_key: str = ""
    r2_endpoint: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "splitcheck-receipts"

    @model_validator(mode="after")
    def fix_database_url(self):
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 6: Create backend/app/database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
```

- [ ] **Step 7: Create backend/app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(title="SplitCheck API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 8: Verify backend starts**

Run: `cd backend && pip install -r requirements.txt && python -m uvicorn app.main:app --port 8000`
Expected: Server starts, `GET /api/health` returns `{"status": "ok"}`

- [ ] **Step 9: Commit**

```bash
git add .gitignore .env.example backend/
git commit -m "feat: backend scaffolding with FastAPI, config, database setup"
```

---

### Task 2: Database Models

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/group.py`
- Create: `backend/app/models/expense.py`
- Create: `backend/app/models/settlement.py`

- [ ] **Step 1: Create backend/app/models/user.py**

```python
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

- [ ] **Step 2: Create backend/app/models/group.py**

```python
import secrets
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    base_currency: Mapped[str] = mapped_column(String(3), default="KZT")
    invite_code: Mapped[str] = mapped_column(
        String(20), unique=True, default=lambda: secrets.token_urlsafe(10)
    )
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    members: Mapped[list["GroupMember"]] = relationship(back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    display_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), default="member")

    group: Mapped["Group"] = relationship(back_populates="members")

    __table_args__ = (
        UniqueConstraint(
            "group_id", "user_id", name="uq_group_member_user"
        ),
    )
```

- [ ] **Step 3: Create backend/app/models/expense.py**

```python
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    paid_by_id: Mapped[int] = mapped_column(ForeignKey("group_members.id"))
    title: Mapped[str] = mapped_column(String(300))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=Decimal("1"))
    receipt_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    split_type: Mapped[str] = mapped_column(String(20))  # equal, by_items, custom
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    items: Mapped[list["ExpenseItem"]] = relationship(
        back_populates="expense", cascade="all, delete-orphan"
    )
    shares: Mapped[list["ExpenseShare"]] = relationship(
        back_populates="expense", cascade="all, delete-orphan"
    )


class ExpenseItem(Base):
    __tablename__ = "expense_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(300))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    expense: Mapped["Expense"] = relationship(back_populates="items")


class ExpenseShare(Base):
    __tablename__ = "expense_shares"

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE")
    )
    member_id: Mapped[int] = mapped_column(ForeignKey("group_members.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    item_id: Mapped[int | None] = mapped_column(
        ForeignKey("expense_items.id", ondelete="SET NULL"), nullable=True
    )

    expense: Mapped["Expense"] = relationship(back_populates="shares")
```

- [ ] **Step 4: Create backend/app/models/settlement.py**

```python
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    from_member_id: Mapped[int] = mapped_column(ForeignKey("group_members.id"))
    to_member_id: Mapped[int] = mapped_column(ForeignKey("group_members.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    is_settled: Mapped[bool] = mapped_column(Boolean, default=False)
    settled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    confirmed_by_to: Mapped[bool] = mapped_column(Boolean, default=False)
```

- [ ] **Step 5: Create backend/app/models/__init__.py**

```python
from app.models.user import Base, User
from app.models.group import Group, GroupMember
from app.models.expense import Expense, ExpenseItem, ExpenseShare
from app.models.settlement import Settlement

__all__ = [
    "Base",
    "User",
    "Group",
    "GroupMember",
    "Expense",
    "ExpenseItem",
    "ExpenseShare",
    "Settlement",
]
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/
git commit -m "feat: add all SQLAlchemy database models"
```

---

### Task 3: Alembic Setup & Initial Migration

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`

- [ ] **Step 1: Initialize alembic**

Run: `cd backend && alembic init alembic`

- [ ] **Step 2: Edit backend/alembic/env.py**

Replace the generated `env.py` with:

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- [ ] **Step 3: Update alembic.ini — remove sqlalchemy.url line**

The `sqlalchemy.url` is provided by `app.config.settings` in `env.py`, so comment out or remove it from `alembic.ini`.

- [ ] **Step 4: Generate initial migration**

Run: `cd backend && alembic revision --autogenerate -m "initial schema"`
Expected: New migration file in `alembic/versions/`

- [ ] **Step 5: Apply migration**

Run: `cd backend && alembic upgrade head`
Expected: All tables created in PostgreSQL

- [ ] **Step 6: Commit**

```bash
git add backend/alembic/ backend/alembic.ini
git commit -m "feat: alembic setup with initial schema migration"
```

---

### Task 4: Telegram Auth & JWT

**Files:**
- Create: `backend/app/auth.py`
- Create: `backend/app/deps.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/auth.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Create backend/app/auth.py**

```python
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

    # Build data-check-string: alphabetically sorted "key=value" joined by \n
    data_check_parts = []
    for key in sorted(parsed.keys()):
        data_check_parts.append(f"{key}={parsed[key][0]}")
    data_check_string = "\n".join(data_check_parts)

    # HMAC-SHA256 with secret derived from bot token
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
    """Decode JWT and return user_id, or None if invalid."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return int(payload["sub"])
    except (jwt.JWTError, KeyError, ValueError):
        return None
```

- [ ] **Step 2: Create backend/app/deps.py**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import decode_access_token
from app.database import get_db
from app.models import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user
```

- [ ] **Step 3: Create backend/app/schemas/__init__.py**

Empty file.

- [ ] **Step 4: Create backend/app/schemas/auth.py**

```python
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
```

- [ ] **Step 5: Create backend/app/api/__init__.py**

Empty file.

- [ ] **Step 6: Create backend/app/api/auth.py**

```python
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

    # Find or create user
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
```

- [ ] **Step 7: Register auth router in main.py**

Replace `backend/app/main.py` with:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.config import settings

app = FastAPI(title="SplitCheck API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 8: Write auth tests — create backend/tests/conftest.py**

```python
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models import Base

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSession() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db():
    async with TestSession() as session:
        yield session
```

- [ ] **Step 9: Write backend/tests/test_auth.py**

```python
import hashlib
import hmac
import json
from urllib.parse import urlencode

import pytest
from app.auth import create_access_token, decode_access_token, validate_telegram_init_data
from app.config import settings


def make_init_data(user_data: dict, bot_token: str = "") -> str:
    """Build a valid Telegram initData string for testing."""
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
        user = {"id": 999, "first_name": "Test"}
        init_data = make_init_data(user) + "&hash=badhash"
        # parse_qs will take last value — but our function pops hash[0]
        # Let's just tamper the hash directly
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
```

- [ ] **Step 10: Run tests**

Run: `cd backend && pip install aiosqlite && python -m pytest tests/test_auth.py -v`
Expected: All tests pass.

- [ ] **Step 11: Commit**

```bash
git add backend/app/auth.py backend/app/deps.py backend/app/schemas/ backend/app/api/ backend/app/main.py backend/tests/
git commit -m "feat: Telegram auth with JWT, validation, and tests"
```

---

## Phase 2: Core API

### Task 5: Groups API & Schemas

**Files:**
- Create: `backend/app/schemas/group.py`
- Create: `backend/app/api/groups.py`
- Create: `backend/tests/test_groups.py`
- Modify: `backend/app/main.py` — add groups router

- [ ] **Step 1: Create backend/app/schemas/group.py**

```python
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


class JoinRequest(BaseModel):
    invite_code: str
    link_to_member_id: int | None = None  # optional: link to existing virtual member
```

- [ ] **Step 2: Create backend/app/api/groups.py**

```python
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
```

- [ ] **Step 3: Register groups router in main.py**

Add to `backend/app/main.py`:

```python
from app.api.groups import router as groups_router

app.include_router(groups_router)
```

- [ ] **Step 4: Write backend/tests/test_groups.py**

```python
import pytest

from app.auth import create_access_token
from app.models import User


@pytest.fixture
async def auth_headers(db):
    user = User(telegram_id=11111, display_name="TestUser")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
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
```

- [ ] **Step 5: Run tests**

Run: `cd backend && python -m pytest tests/test_groups.py -v`
Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/group.py backend/app/api/groups.py backend/app/main.py backend/tests/test_groups.py
git commit -m "feat: groups API with CRUD, join, virtual members"
```

---

### Task 6: Expenses API & Schemas

**Files:**
- Create: `backend/app/schemas/expense.py`
- Create: `backend/app/api/expenses.py`
- Create: `backend/tests/test_expenses.py`
- Modify: `backend/app/main.py` — add expenses router

- [ ] **Step 1: Create backend/app/schemas/expense.py**

```python
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ExpenseItemCreate(BaseModel):
    name: str
    price: Decimal
    quantity: int = 1


class ShareCreate(BaseModel):
    member_id: int
    amount: Decimal
    item_id: int | None = None


class ExpenseCreate(BaseModel):
    title: str
    total_amount: Decimal
    currency: str
    exchange_rate: Decimal = Decimal("1")
    paid_by_id: int
    split_type: str  # equal, by_items, custom
    # For equal split: list of member_ids who share the expense
    split_among: list[int] | None = None
    # For by_items / custom: explicit items and shares
    items: list[ExpenseItemCreate] | None = None
    shares: list[ShareCreate] | None = None
    receipt_image_url: str | None = None


class ExpenseItemOut(BaseModel):
    id: int
    name: str
    price: Decimal
    quantity: int

    model_config = {"from_attributes": True}


class ExpenseShareOut(BaseModel):
    id: int
    member_id: int
    amount: Decimal
    item_id: int | None

    model_config = {"from_attributes": True}


class ExpenseOut(BaseModel):
    id: int
    group_id: int
    paid_by_id: int
    title: str
    total_amount: Decimal
    currency: str
    exchange_rate: Decimal
    receipt_image_url: str | None
    split_type: str
    created_at: datetime
    items: list[ExpenseItemOut] = []
    shares: list[ExpenseShareOut] = []

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Create backend/app/api/expenses.py**

```python
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Expense, ExpenseItem, ExpenseShare, Group, GroupMember, User
from app.schemas.expense import ExpenseCreate, ExpenseOut

router = APIRouter(tags=["expenses"])


@router.get("/api/groups/{group_id}/expenses", response_model=list[ExpenseOut])
async def list_expenses(
    group_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_membership(group_id, user.id, db)
    result = await db.execute(
        select(Expense)
        .where(Expense.group_id == group_id)
        .options(selectinload(Expense.items), selectinload(Expense.shares))
        .order_by(Expense.created_at.desc())
    )
    return result.scalars().all()


@router.post("/api/groups/{group_id}/expenses", response_model=ExpenseOut, status_code=201)
async def create_expense(
    group_id: int,
    body: ExpenseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_membership(group_id, user.id, db)

    expense = Expense(
        group_id=group_id,
        paid_by_id=body.paid_by_id,
        title=body.title,
        total_amount=body.total_amount,
        currency=body.currency,
        exchange_rate=body.exchange_rate,
        receipt_image_url=body.receipt_image_url,
        split_type=body.split_type,
    )
    db.add(expense)
    await db.flush()

    if body.split_type == "equal" and body.split_among:
        share_amount = (body.total_amount / len(body.split_among)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        for member_id in body.split_among:
            share = ExpenseShare(
                expense_id=expense.id, member_id=member_id, amount=share_amount
            )
            db.add(share)

    elif body.split_type == "by_items" and body.items:
        for item_data in body.items:
            item = ExpenseItem(
                expense_id=expense.id,
                name=item_data.name,
                price=item_data.price,
                quantity=item_data.quantity,
            )
            db.add(item)
            await db.flush()

        if body.shares:
            for share_data in body.shares:
                share = ExpenseShare(
                    expense_id=expense.id,
                    member_id=share_data.member_id,
                    amount=share_data.amount,
                    item_id=share_data.item_id,
                )
                db.add(share)

    elif body.split_type == "custom" and body.shares:
        for share_data in body.shares:
            share = ExpenseShare(
                expense_id=expense.id,
                member_id=share_data.member_id,
                amount=share_data.amount,
            )
            db.add(share)

    await db.commit()

    result = await db.execute(
        select(Expense)
        .where(Expense.id == expense.id)
        .options(selectinload(Expense.items), selectinload(Expense.shares))
    )
    return result.scalar_one()


@router.get("/api/expenses/{expense_id}", response_model=ExpenseOut)
async def get_expense(
    expense_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Expense)
        .where(Expense.id == expense_id)
        .options(selectinload(Expense.items), selectinload(Expense.shares))
    )
    expense = result.scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    await _verify_membership(expense.group_id, user.id, db)
    return expense


@router.delete("/api/expenses/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    await _verify_membership(expense.group_id, user.id, db)
    await db.delete(expense)
    await db.commit()


async def _verify_membership(group_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.user_id == user_id
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Not a member of this group")
```

- [ ] **Step 3: Register expenses router in main.py**

Add to `backend/app/main.py`:

```python
from app.api.expenses import router as expenses_router

app.include_router(expenses_router)
```

- [ ] **Step 4: Write backend/tests/test_expenses.py**

```python
import pytest
from decimal import Decimal

from app.auth import create_access_token
from app.models import User, Group, GroupMember


@pytest.fixture
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
```

- [ ] **Step 5: Run tests**

Run: `cd backend && python -m pytest tests/test_expenses.py -v`
Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/expense.py backend/app/api/expenses.py backend/app/main.py backend/tests/test_expenses.py
git commit -m "feat: expenses API with equal, custom, and by_items split modes"
```

---

### Task 7: Settlement Calculator (Pure Logic)

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/settlement_calculator.py`
- Create: `backend/tests/test_settlement_calculator.py`

- [ ] **Step 1: Create backend/app/services/__init__.py**

Empty file.

- [ ] **Step 2: Write failing test — backend/tests/test_settlement_calculator.py**

```python
from decimal import Decimal

from app.services.settlement_calculator import calculate_balances, minimize_settlements


class TestCalculateBalances:
    def test_equal_split_two_people(self):
        # Alice paid 1000, split equally between Alice and Bob
        expenses = [
            {
                "paid_by_id": 1,
                "total_amount": Decimal("1000"),
                "exchange_rate": Decimal("1"),
                "shares": [
                    {"member_id": 1, "amount": Decimal("500")},
                    {"member_id": 2, "amount": Decimal("500")},
                ],
            }
        ]
        balances = calculate_balances(expenses)
        # Alice paid 1000, owes 500 => net +500
        # Bob paid 0, owes 500 => net -500
        assert balances[1] == Decimal("500")
        assert balances[2] == Decimal("-500")

    def test_multiple_expenses(self):
        expenses = [
            {
                "paid_by_id": 1,
                "total_amount": Decimal("3000"),
                "exchange_rate": Decimal("1"),
                "shares": [
                    {"member_id": 1, "amount": Decimal("1000")},
                    {"member_id": 2, "amount": Decimal("1000")},
                    {"member_id": 3, "amount": Decimal("1000")},
                ],
            },
            {
                "paid_by_id": 2,
                "total_amount": Decimal("1500"),
                "exchange_rate": Decimal("1"),
                "shares": [
                    {"member_id": 1, "amount": Decimal("750")},
                    {"member_id": 2, "amount": Decimal("750")},
                ],
            },
        ]
        balances = calculate_balances(expenses)
        # Alice: paid 3000, owes 1000+750=1750 => net +1250
        # Bob: paid 1500, owes 1000+750=1750 => net -250
        # Charlie: paid 0, owes 1000 => net -1000
        assert balances[1] == Decimal("1250")
        assert balances[2] == Decimal("-250")
        assert balances[3] == Decimal("-1000")

    def test_with_exchange_rate(self):
        expenses = [
            {
                "paid_by_id": 1,
                "total_amount": Decimal("100"),
                "exchange_rate": Decimal("450"),  # 1 USD = 450 KZT
                "shares": [
                    {"member_id": 1, "amount": Decimal("50")},
                    {"member_id": 2, "amount": Decimal("50")},
                ],
            }
        ]
        balances = calculate_balances(expenses)
        # In base currency: paid 100*450=45000, each owes 50*450=22500
        assert balances[1] == Decimal("22500")
        assert balances[2] == Decimal("-22500")


class TestMinimizeSettlements:
    def test_simple_two_people(self):
        balances = {1: Decimal("500"), 2: Decimal("-500")}
        settlements = minimize_settlements(balances)
        assert len(settlements) == 1
        assert settlements[0] == (2, 1, Decimal("500"))

    def test_four_people_minimized(self):
        # From design spec example:
        # Alice +8500, Boris +1200, Vika -3700, Gena -6000
        balances = {
            1: Decimal("8500"),
            2: Decimal("1200"),
            3: Decimal("-3700"),
            4: Decimal("-6000"),
        }
        settlements = minimize_settlements(balances)
        # Should be 3 transfers max (could be 2-3)
        assert len(settlements) <= 3

        # Verify net effect: each person's balance zeroes out
        net = dict(balances)
        for from_id, to_id, amount in settlements:
            net[from_id] += amount
            net[to_id] -= amount
        for v in net.values():
            assert v == Decimal("0")

    def test_already_settled(self):
        balances = {1: Decimal("0"), 2: Decimal("0")}
        settlements = minimize_settlements(balances)
        assert len(settlements) == 0

    def test_three_way_circle(self):
        # A owes B 100, B owes C 100, C owes A 100 => all zero
        balances = {1: Decimal("0"), 2: Decimal("0"), 3: Decimal("0")}
        settlements = minimize_settlements(balances)
        assert len(settlements) == 0
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_settlement_calculator.py -v`
Expected: ImportError — module not found.

- [ ] **Step 4: Implement backend/app/services/settlement_calculator.py**

```python
from decimal import Decimal
from collections import defaultdict


def calculate_balances(expenses: list[dict]) -> dict[int, Decimal]:
    """Calculate net balance for each member across all expenses.

    Positive = others owe them. Negative = they owe others.
    All amounts converted to base currency using exchange_rate.
    """
    balances: dict[int, Decimal] = defaultdict(Decimal)

    for expense in expenses:
        paid_by = expense["paid_by_id"]
        rate = expense["exchange_rate"]
        total_in_base = expense["total_amount"] * rate

        # Payer gets credited for the full amount
        balances[paid_by] += total_in_base

        # Each share debits the member
        for share in expense["shares"]:
            member_id = share["member_id"]
            amount_in_base = share["amount"] * rate
            balances[member_id] -= amount_in_base

    return dict(balances)


def minimize_settlements(balances: dict[int, Decimal]) -> list[tuple[int, int, Decimal]]:
    """Minimize the number of transfers to settle all debts.

    Returns list of (from_member_id, to_member_id, amount) tuples.
    Uses greedy algorithm: match largest debtor with largest creditor.
    """
    # Separate into debtors (negative balance) and creditors (positive balance)
    debtors = []  # (member_id, abs_amount)
    creditors = []  # (member_id, amount)

    for member_id, balance in balances.items():
        if balance < 0:
            debtors.append([member_id, -balance])
        elif balance > 0:
            creditors.append([member_id, balance])

    # Sort descending by amount
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    settlements = []
    i, j = 0, 0

    while i < len(debtors) and j < len(creditors):
        debtor_id, debt = debtors[i]
        creditor_id, credit = creditors[j]

        transfer = min(debt, credit)
        if transfer > 0:
            settlements.append((debtor_id, creditor_id, transfer))

        debtors[i][1] -= transfer
        creditors[j][1] -= transfer

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return settlements
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_settlement_calculator.py -v`
Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/ backend/tests/test_settlement_calculator.py
git commit -m "feat: settlement calculator with balance computation and transaction minimization"
```

---

### Task 8: Balances & Settlements API

**Files:**
- Create: `backend/app/schemas/settlement.py`
- Create: `backend/app/api/settlements.py`
- Modify: `backend/app/main.py` — add settlements router

- [ ] **Step 1: Create backend/app/schemas/settlement.py**

```python
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BalanceOut(BaseModel):
    member_id: int
    display_name: str
    balance: Decimal  # positive = owed to them, negative = they owe


class SettlementOut(BaseModel):
    id: int
    from_member_id: int
    from_member_name: str
    to_member_id: int
    to_member_name: str
    amount: Decimal
    currency: str
    is_settled: bool
    settled_at: datetime | None
    confirmed_by_to: bool

    model_config = {"from_attributes": True}


class SettlementUpdate(BaseModel):
    is_settled: bool | None = None
    confirmed_by_to: bool | None = None
```

- [ ] **Step 2: Create backend/app/api/settlements.py**

```python
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Expense,
    ExpenseShare,
    Group,
    GroupMember,
    Settlement,
    User,
)
from app.schemas.settlement import BalanceOut, SettlementOut, SettlementUpdate
from app.services.settlement_calculator import calculate_balances, minimize_settlements

router = APIRouter(tags=["settlements"])


@router.get("/api/groups/{group_id}/balances", response_model=list[BalanceOut])
async def get_balances(
    group_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_membership(group_id, user.id, db)

    expenses_data = await _load_expenses_for_calculation(group_id, db)
    balances = calculate_balances(expenses_data)

    members = await _load_members(group_id, db)
    member_names = {m.id: m.display_name for m in members}

    result = []
    for member in members:
        result.append(
            BalanceOut(
                member_id=member.id,
                display_name=member.display_name,
                balance=balances.get(member.id, 0),
            )
        )
    return result


@router.get("/api/groups/{group_id}/settlements", response_model=list[SettlementOut])
async def get_settlements(
    group_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_membership(group_id, user.id, db)

    # Recalculate optimal settlements
    expenses_data = await _load_expenses_for_calculation(group_id, db)
    balances = calculate_balances(expenses_data)
    optimal = minimize_settlements(balances)

    members = await _load_members(group_id, db)
    member_names = {m.id: m.display_name for m in members}

    group = await db.get(Group, group_id)

    # Delete old unsettled settlements and recreate
    await db.execute(
        delete(Settlement).where(
            Settlement.group_id == group_id, Settlement.is_settled == False
        )
    )

    # Load existing settled ones to preserve them
    result_settled = await db.execute(
        select(Settlement).where(
            Settlement.group_id == group_id, Settlement.is_settled == True
        )
    )
    settled = result_settled.scalars().all()

    # Create new unsettled settlements
    new_settlements = []
    for from_id, to_id, amount in optimal:
        s = Settlement(
            group_id=group_id,
            from_member_id=from_id,
            to_member_id=to_id,
            amount=amount,
            currency=group.base_currency,
        )
        db.add(s)
        new_settlements.append(s)

    await db.commit()

    # Build response
    all_settlements = list(settled) + new_settlements
    for s in all_settlements:
        await db.refresh(s)

    return [
        SettlementOut(
            id=s.id,
            from_member_id=s.from_member_id,
            from_member_name=member_names.get(s.from_member_id, "?"),
            to_member_id=s.to_member_id,
            to_member_name=member_names.get(s.to_member_id, "?"),
            amount=s.amount,
            currency=s.currency,
            is_settled=s.is_settled,
            settled_at=s.settled_at,
            confirmed_by_to=s.confirmed_by_to,
        )
        for s in all_settlements
    ]


@router.patch("/api/settlements/{settlement_id}", response_model=SettlementOut)
async def update_settlement(
    settlement_id: int,
    body: SettlementUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settlement = await db.get(Settlement, settlement_id)
    if settlement is None:
        raise HTTPException(status_code=404, detail="Settlement not found")

    await _verify_membership(settlement.group_id, user.id, db)

    members = await _load_members(settlement.group_id, db)
    member_names = {m.id: m.display_name for m in members}

    if body.is_settled is not None:
        settlement.is_settled = body.is_settled
        settlement.settled_at = datetime.now(timezone.utc) if body.is_settled else None
    if body.confirmed_by_to is not None:
        settlement.confirmed_by_to = body.confirmed_by_to

    await db.commit()
    await db.refresh(settlement)

    return SettlementOut(
        id=settlement.id,
        from_member_id=settlement.from_member_id,
        from_member_name=member_names.get(settlement.from_member_id, "?"),
        to_member_id=settlement.to_member_id,
        to_member_name=member_names.get(settlement.to_member_id, "?"),
        amount=settlement.amount,
        currency=settlement.currency,
        is_settled=settlement.is_settled,
        settled_at=settlement.settled_at,
        confirmed_by_to=settlement.confirmed_by_to,
    )


async def _verify_membership(group_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.user_id == user_id
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Not a member")


async def _load_members(group_id: int, db: AsyncSession) -> list[GroupMember]:
    result = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id)
    )
    return result.scalars().all()


async def _load_expenses_for_calculation(
    group_id: int, db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(Expense)
        .where(Expense.group_id == group_id)
        .options(selectinload(Expense.shares))
    )
    expenses = result.scalars().all()

    return [
        {
            "paid_by_id": e.paid_by_id,
            "total_amount": e.total_amount,
            "exchange_rate": e.exchange_rate,
            "shares": [
                {"member_id": s.member_id, "amount": s.amount} for s in e.shares
            ],
        }
        for e in expenses
    ]
```

- [ ] **Step 3: Register settlements router in main.py**

Add to `backend/app/main.py`:

```python
from app.api.settlements import router as settlements_router

app.include_router(settlements_router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/schemas/settlement.py backend/app/api/settlements.py backend/app/main.py
git commit -m "feat: balances and settlements API with transaction minimization"
```

---

## Phase 3: Receipt Scanning & Currency

### Task 9: Receipt Scanner Service (Claude Vision)

**Files:**
- Create: `backend/app/services/receipt_scanner.py`
- Create: `backend/app/schemas/receipt.py`
- Create: `backend/app/api/receipts.py`
- Create: `backend/tests/test_receipts.py`
- Modify: `backend/app/main.py` — add receipts router

- [ ] **Step 1: Create backend/app/schemas/receipt.py**

```python
from decimal import Decimal

from pydantic import BaseModel


class ReceiptItem(BaseModel):
    name: str
    price: Decimal
    quantity: int = 1


class ReceiptScanResponse(BaseModel):
    items: list[ReceiptItem]
    total: Decimal | None = None
    tax: Decimal | None = None
    tips: Decimal | None = None
    currency: str | None = None
    raw_text: str | None = None
```

- [ ] **Step 2: Create backend/app/services/receipt_scanner.py**

```python
import base64
import json
from decimal import Decimal
from pathlib import Path

import anthropic

from app.config import settings
from app.schemas.receipt import ReceiptItem, ReceiptScanResponse

RECEIPT_PROMPT = """Analyze this receipt image. Extract all line items with their names, prices, and quantities.

Return a JSON object with this exact structure:
{
  "items": [
    {"name": "Item name", "price": 1234.56, "quantity": 1}
  ],
  "total": 1234.56,
  "tax": 0,
  "tips": 0,
  "currency": "KZT"
}

Rules:
- price is per-unit price, not total for the line
- quantity defaults to 1 if not shown
- currency should be the 3-letter ISO code if identifiable, null otherwise
- total is the final total on the receipt
- tax and tips are 0 if not shown
- Return ONLY the JSON, no markdown, no explanation"""


async def scan_receipt(image_bytes: bytes, media_type: str) -> ReceiptScanResponse:
    """Send receipt image to Claude Vision API and parse the response."""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": RECEIPT_PROMPT},
                ],
            }
        ],
    )

    response_text = message.content[0].text.strip()
    # Handle potential markdown code blocks in response
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    data = json.loads(response_text)

    return ReceiptScanResponse(
        items=[
            ReceiptItem(
                name=item["name"],
                price=Decimal(str(item["price"])),
                quantity=item.get("quantity", 1),
            )
            for item in data.get("items", [])
        ],
        total=Decimal(str(data["total"])) if data.get("total") else None,
        tax=Decimal(str(data["tax"])) if data.get("tax") else None,
        tips=Decimal(str(data["tips"])) if data.get("tips") else None,
        currency=data.get("currency"),
    )
```

- [ ] **Step 3: Create backend/app/api/receipts.py**

```python
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.deps import get_current_user
from app.models import User
from app.schemas.receipt import ReceiptScanResponse
from app.services.receipt_scanner import scan_receipt

router = APIRouter(prefix="/api/receipts", tags=["receipts"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/scan", response_model=ReceiptScanResponse)
async def scan_receipt_endpoint(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type: {file.content_type}. Use JPEG, PNG, WebP, or GIF.",
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image too large (max 10 MB)")

    try:
        result = await scan_receipt(image_bytes, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse receipt: {e}")

    return result
```

- [ ] **Step 4: Register receipts router in main.py**

Add to `backend/app/main.py`:

```python
from app.api.receipts import router as receipts_router

app.include_router(receipts_router)
```

- [ ] **Step 5: Write backend/tests/test_receipts.py (unit test with mocked API)**

```python
import json
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.services.receipt_scanner import scan_receipt


@pytest.mark.asyncio
class TestReceiptScanner:
    async def test_scan_receipt_parses_response(self):
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text=json.dumps(
                    {
                        "items": [
                            {"name": "Pizza", "price": 3200, "quantity": 1},
                            {"name": "Latte", "price": 700, "quantity": 2},
                        ],
                        "total": 4600,
                        "tax": 0,
                        "tips": 0,
                        "currency": "KZT",
                    }
                )
            )
        ]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("app.services.receipt_scanner.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await scan_receipt(b"fake-image-bytes", "image/jpeg")

        assert len(result.items) == 2
        assert result.items[0].name == "Pizza"
        assert result.items[0].price == Decimal("3200")
        assert result.items[1].quantity == 2
        assert result.total == Decimal("4600")
        assert result.currency == "KZT"
```

- [ ] **Step 6: Run tests**

Run: `cd backend && python -m pytest tests/test_receipts.py -v`
Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add backend/app/schemas/receipt.py backend/app/services/receipt_scanner.py backend/app/api/receipts.py backend/app/main.py backend/tests/test_receipts.py
git commit -m "feat: receipt scanning via Claude Vision API with structured parsing"
```

---

### Task 10: Currency Service

**Files:**
- Create: `backend/app/services/currency.py`
- Create: `backend/app/api/currencies.py`
- Modify: `backend/app/main.py` — add currencies router

- [ ] **Step 1: Create backend/app/services/currency.py**

```python
import time

import httpx

# In-memory cache: {base_currency: (rates_dict, timestamp)}
_cache: dict[str, tuple[dict[str, float], float]] = {}
CACHE_TTL = 3600  # 1 hour


async def get_exchange_rates(base: str = "USD") -> dict[str, float]:
    """Fetch exchange rates from a free API, with 1-hour cache."""
    now = time.time()
    if base in _cache:
        rates, cached_at = _cache[base]
        if now - cached_at < CACHE_TTL:
            return rates

    url = f"https://open.er-api.com/v6/latest/{base}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    rates = data.get("rates", {})
    _cache[base] = (rates, now)
    return rates
```

- [ ] **Step 2: Create backend/app/api/currencies.py**

```python
from fastapi import APIRouter, Query

from app.services.currency import get_exchange_rates

router = APIRouter(prefix="/api/currencies", tags=["currencies"])


@router.get("/rates")
async def get_rates(base: str = Query("USD", max_length=3)):
    rates = await get_exchange_rates(base.upper())
    return {"base": base.upper(), "rates": rates}
```

- [ ] **Step 3: Register currencies router in main.py**

Add to `backend/app/main.py`:

```python
from app.api.currencies import router as currencies_router

app.include_router(currencies_router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/currency.py backend/app/api/currencies.py backend/app/main.py
git commit -m "feat: currency exchange rates API with in-memory cache"
```

---

## Phase 4: Frontend Foundation

### Task 11: Frontend Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`

- [ ] **Step 1: Create frontend/package.json**

```json
{
  "name": "splitcheck-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.13",
    "vue-router": "^4.5.1",
    "pinia": "^3.0.2",
    "axios": "^1.9.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.4",
    "vite": "^6.3.5",
    "tailwindcss": "^3.4.17",
    "postcss": "^8.5.3",
    "autoprefixer": "^10.4.21"
  }
}
```

- [ ] **Step 2: Create frontend/index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>SplitCheck</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 3: Create frontend/vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

- [ ] **Step 4: Create frontend/tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        primary: '#4f46e5',
        'primary-dark': '#4338ca',
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 5: Create frontend/postcss.config.js**

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 6: Create frontend/src/main.js**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 7: Create frontend/src/style.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--tg-theme-bg-color, #ffffff);
  color: var(--tg-theme-text-color, #111827);
}
```

- [ ] **Step 8: Create frontend/src/router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'my-trips', component: () => import('../views/MyTrips.vue') },
  { path: '/create', name: 'create-group', component: () => import('../views/CreateGroup.vue') },
  { path: '/trip/:id', name: 'trip-detail', component: () => import('../views/TripDetail.vue') },
  { path: '/trip/:id/expense', name: 'add-expense', component: () => import('../views/AddExpense.vue') },
  { path: '/trip/:id/scan', name: 'scan-receipt', component: () => import('../views/ScanReceipt.vue') },
  { path: '/trip/:id/settings', name: 'group-settings', component: () => import('../views/GroupSettings.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

- [ ] **Step 9: Create frontend/src/App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 10: Install dependencies and verify**

Run: `cd frontend && npm install && npm run dev`
Expected: Vite dev server starts on `http://localhost:5173`

- [ ] **Step 11: Commit**

```bash
git add frontend/
git commit -m "feat: frontend scaffolding with Vue 3, Vite, Tailwind, Pinia, Vue Router"
```

---

### Task 12: API Client & Auth Store

**Files:**
- Create: `frontend/src/api/client.js`
- Create: `frontend/src/api/auth.js`
- Create: `frontend/src/stores/auth.js`
- Create: `frontend/src/composables/useTelegram.js`

- [ ] **Step 1: Create frontend/src/composables/useTelegram.js**

```javascript
export function useTelegram() {
  const tg = window.Telegram?.WebApp

  function ready() {
    tg?.ready()
    tg?.expand()
  }

  function getInitData() {
    return tg?.initData || ''
  }

  function getUserName() {
    const user = tg?.initDataUnsafe?.user
    if (!user) return 'Guest'
    return [user.first_name, user.last_name].filter(Boolean).join(' ')
  }

  function showAlert(message) {
    if (tg?.showAlert) {
      tg.showAlert(message)
    } else {
      alert(message)
    }
  }

  function hapticFeedback(type = 'impact') {
    tg?.HapticFeedback?.[type === 'impact' ? 'impactOccurred' : 'notificationOccurred']?.(
      type === 'impact' ? 'medium' : 'success'
    )
  }

  return { tg, ready, getInitData, getUserName, showAlert, hapticFeedback }
}
```

- [ ] **Step 2: Create frontend/src/api/client.js**

```javascript
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export default client
```

- [ ] **Step 3: Create frontend/src/api/auth.js**

```javascript
import client from './client'

export async function loginWithTelegram(initData) {
  const { data } = await client.post('/auth/telegram', { init_data: initData })
  return data
}

export async function getMe() {
  const { data } = await client.get('/auth/me')
  return data
}
```

- [ ] **Step 4: Create frontend/src/stores/auth.js**

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginWithTelegram, getMe } from '../api/auth'
import { useTelegram } from '../composables/useTelegram'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const loading = ref(false)

  async function login() {
    loading.value = true
    try {
      const { getInitData } = useTelegram()
      const initData = getInitData()

      if (!initData) {
        console.warn('No Telegram initData — running outside Telegram')
        return false
      }

      const result = await loginWithTelegram(initData)
      localStorage.setItem('access_token', result.access_token)
      user.value = { id: result.user_id, display_name: result.display_name }
      isLoggedIn.value = true
      return true
    } catch (e) {
      console.error('Auth failed:', e)
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    try {
      user.value = await getMe()
      isLoggedIn.value = true
    } catch {
      isLoggedIn.value = false
    }
  }

  async function init() {
    const token = localStorage.getItem('access_token')
    if (token) {
      await fetchUser()
    }
    if (!isLoggedIn.value) {
      await login()
    }
  }

  return { user, isLoggedIn, loading, login, init }
})
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/ frontend/src/stores/auth.js frontend/src/composables/useTelegram.js
git commit -m "feat: API client with JWT interceptor, Telegram auth store"
```

---

### Task 13: API Modules (Groups, Expenses, Receipts, Settlements)

**Files:**
- Create: `frontend/src/api/groups.js`
- Create: `frontend/src/api/expenses.js`
- Create: `frontend/src/api/receipts.js`
- Create: `frontend/src/api/settlements.js`
- Create: `frontend/src/stores/groups.js`

- [ ] **Step 1: Create frontend/src/api/groups.js**

```javascript
import client from './client'

export async function fetchGroups() {
  const { data } = await client.get('/groups')
  return data
}

export async function createGroup(payload) {
  const { data } = await client.post('/groups', payload)
  return data
}

export async function getGroup(id) {
  const { data } = await client.get(`/groups/${id}`)
  return data
}

export async function updateGroup(id, payload) {
  const { data } = await client.patch(`/groups/${id}`, payload)
  return data
}

export async function joinGroup(id, inviteCode, linkToMemberId = null) {
  const { data } = await client.post(`/groups/${id}/join`, {
    invite_code: inviteCode,
    link_to_member_id: linkToMemberId,
  })
  return data
}

export async function addMember(groupId, displayName) {
  const { data } = await client.post(`/groups/${groupId}/members`, {
    display_name: displayName,
  })
  return data
}
```

- [ ] **Step 2: Create frontend/src/api/expenses.js**

```javascript
import client from './client'

export async function fetchExpenses(groupId) {
  const { data } = await client.get(`/groups/${groupId}/expenses`)
  return data
}

export async function createExpense(groupId, payload) {
  const { data } = await client.post(`/groups/${groupId}/expenses`, payload)
  return data
}

export async function getExpense(id) {
  const { data } = await client.get(`/expenses/${id}`)
  return data
}

export async function deleteExpense(id) {
  await client.delete(`/expenses/${id}`)
}
```

- [ ] **Step 3: Create frontend/src/api/receipts.js**

```javascript
import client from './client'

export async function scanReceipt(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/receipts/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
```

- [ ] **Step 4: Create frontend/src/api/settlements.js**

```javascript
import client from './client'

export async function fetchBalances(groupId) {
  const { data } = await client.get(`/groups/${groupId}/balances`)
  return data
}

export async function fetchSettlements(groupId) {
  const { data } = await client.get(`/groups/${groupId}/settlements`)
  return data
}

export async function updateSettlement(id, payload) {
  const { data } = await client.patch(`/settlements/${id}`, payload)
  return data
}
```

- [ ] **Step 5: Create frontend/src/stores/groups.js**

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchGroups, getGroup } from '../api/groups'

export const useGroupsStore = defineStore('groups', () => {
  const groups = ref([])
  const currentGroup = ref(null)
  const loading = ref(false)

  const activeGroups = () => groups.value.filter((g) => g.status === 'active')
  const archivedGroups = () => groups.value.filter((g) => g.status === 'archived')

  async function loadGroups() {
    loading.value = true
    try {
      groups.value = await fetchGroups()
    } finally {
      loading.value = false
    }
  }

  async function loadGroup(id) {
    loading.value = true
    try {
      currentGroup.value = await getGroup(id)
    } finally {
      loading.value = false
    }
  }

  return { groups, currentGroup, loading, activeGroups, archivedGroups, loadGroups, loadGroup }
})
```

- [ ] **Step 6: Create frontend/src/utils/format.js**

```javascript
export function formatAmount(amount, currency = 'KZT') {
  const num = Number(amount)
  const symbols = { KZT: '₸', USD: '$', EUR: '€', RUB: '₽', GBP: '£' }
  const symbol = symbols[currency] || currency
  return `${num.toLocaleString('ru-RU', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}${symbol}`
}

export function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/api/ frontend/src/stores/groups.js frontend/src/utils/format.js
git commit -m "feat: frontend API modules, groups store, formatting utils"
```

---

## Phase 5: Frontend Views

### Task 14: MyTrips View + GroupCard Component

**Files:**
- Create: `frontend/src/views/MyTrips.vue`
- Create: `frontend/src/components/GroupCard.vue`

- [ ] **Step 1: Create frontend/src/components/GroupCard.vue**

```vue
<template>
  <router-link
    :to="{ name: 'trip-detail', params: { id: group.id } }"
    class="block bg-gray-50 rounded-xl p-4 border-l-4 active:bg-gray-100 no-underline"
    :class="group.status === 'archived' ? 'border-gray-300 opacity-60' : 'border-primary'"
  >
    <div class="flex justify-between items-start">
      <div>
        <div class="font-semibold text-[15px]">{{ group.name }}</div>
        <div class="text-gray-500 text-xs mt-0.5">
          {{ group.members.length }} participants · {{ group.base_currency }}
        </div>
      </div>
      <div v-if="group.status === 'archived'" class="text-xs text-gray-400">
        Archived
      </div>
    </div>
    <div class="flex mt-2.5 gap-1">
      <div
        v-for="member in group.members.slice(0, 6)"
        :key="member.id"
        class="w-7 h-7 rounded-full bg-primary text-white text-[10px] flex items-center justify-center font-semibold"
        :style="{ backgroundColor: memberColor(member.id) }"
      >
        {{ initials(member.display_name) }}
      </div>
      <div
        v-if="group.members.length > 6"
        class="w-7 h-7 rounded-full bg-gray-300 text-gray-600 text-[10px] flex items-center justify-center"
      >
        +{{ group.members.length - 6 }}
      </div>
    </div>
  </router-link>
</template>

<script setup>
const props = defineProps({ group: Object })

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

function memberColor(id) {
  return colors[id % colors.length]
}

function initials(name) {
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}
</script>
```

- [ ] **Step 2: Create frontend/src/views/MyTrips.vue**

```vue
<template>
  <div class="min-h-screen pb-20">
    <div class="px-4 pt-4 pb-2">
      <h1 class="text-xl font-bold">My Trips</h1>
    </div>

    <!-- Tabs -->
    <div class="flex border-b-2 border-gray-200 px-4">
      <button
        class="flex-1 py-3 text-center font-semibold text-sm transition-colors"
        :class="tab === 'active' ? 'text-primary border-b-2 border-primary -mb-[2px]' : 'text-gray-400'"
        @click="tab = 'active'"
      >
        Active
      </button>
      <button
        class="flex-1 py-3 text-center font-semibold text-sm transition-colors"
        :class="tab === 'archived' ? 'text-primary border-b-2 border-primary -mb-[2px]' : 'text-gray-400'"
        @click="tab = 'archived'"
      >
        Archive
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="p-8 text-center text-gray-400">Loading...</div>

    <!-- Group list -->
    <div v-else class="px-4 pt-3 space-y-2.5">
      <GroupCard
        v-for="group in displayedGroups"
        :key="group.id"
        :group="group"
      />
      <div v-if="displayedGroups.length === 0" class="text-center text-gray-400 py-12">
        {{ tab === 'active' ? 'No active trips' : 'No archived trips' }}
      </div>
    </div>

    <!-- FAB -->
    <div class="fixed bottom-6 left-0 right-0 flex justify-center">
      <router-link
        :to="{ name: 'create-group' }"
        class="bg-primary text-white px-6 py-3 rounded-full font-semibold text-sm shadow-lg active:bg-primary-dark no-underline"
      >
        + New Trip
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGroupsStore } from '../stores/groups'
import { useAuthStore } from '../stores/auth'
import { useTelegram } from '../composables/useTelegram'
import GroupCard from '../components/GroupCard.vue'

const store = useGroupsStore()
const auth = useAuthStore()
const { ready } = useTelegram()

const tab = ref('active')

const displayedGroups = computed(() =>
  tab.value === 'active' ? store.activeGroups() : store.archivedGroups()
)

onMounted(async () => {
  ready()
  await auth.init()
  await store.loadGroups()
})
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/MyTrips.vue frontend/src/components/GroupCard.vue
git commit -m "feat: MyTrips view with active/archived tabs and GroupCard component"
```

---

### Task 15: CreateGroup View

**Files:**
- Create: `frontend/src/views/CreateGroup.vue`
- Create: `frontend/src/composables/useCurrency.js`

- [ ] **Step 1: Create frontend/src/composables/useCurrency.js**

```javascript
export const CURRENCIES = [
  { code: 'KZT', name: 'Tenge', symbol: '₸' },
  { code: 'USD', name: 'US Dollar', symbol: '$' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'RUB', name: 'Ruble', symbol: '₽' },
  { code: 'GBP', name: 'Pound', symbol: '£' },
  { code: 'TRY', name: 'Turkish Lira', symbol: '₺' },
  { code: 'THB', name: 'Thai Baht', symbol: '฿' },
  { code: 'GEL', name: 'Georgian Lari', symbol: '₾' },
]

export function useCurrency() {
  function getSymbol(code) {
    return CURRENCIES.find((c) => c.code === code)?.symbol || code
  }
  return { CURRENCIES, getSymbol }
}
```

- [ ] **Step 2: Create frontend/src/views/CreateGroup.vue**

```vue
<template>
  <div class="min-h-screen px-4 pt-4">
    <h1 class="text-xl font-bold mb-6">New Trip</h1>

    <form @submit.prevent="submit" class="space-y-5">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Trip name</label>
        <input
          v-model="name"
          type="text"
          placeholder="e.g. Bali with friends"
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
          required
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Base currency</label>
        <select
          v-model="currency"
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-primary outline-none"
        >
          <option v-for="c in CURRENCIES" :key="c.code" :value="c.code">
            {{ c.symbol }} {{ c.code }} — {{ c.name }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Participants</label>
        <div class="space-y-2">
          <div
            v-for="(member, i) in members"
            :key="i"
            class="flex items-center gap-2"
          >
            <input
              v-model="members[i]"
              type="text"
              :placeholder="`Participant ${i + 1}`"
              class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary"
            />
            <button
              v-if="members.length > 1"
              type="button"
              @click="members.splice(i, 1)"
              class="text-red-400 text-lg px-2"
            >×</button>
          </div>
        </div>
        <button
          type="button"
          @click="members.push('')"
          class="mt-2 text-primary text-sm font-medium"
        >
          + Add participant
        </button>
      </div>

      <button
        type="submit"
        :disabled="saving"
        class="w-full bg-primary text-white py-3 rounded-xl font-semibold text-sm disabled:opacity-50"
      >
        {{ saving ? 'Creating...' : 'Create Trip' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createGroup, addMember } from '../api/groups'
import { useCurrency } from '../composables/useCurrency'

const router = useRouter()
const { CURRENCIES } = useCurrency()

const name = ref('')
const currency = ref('KZT')
const members = ref([''])
const saving = ref(false)

async function submit() {
  saving.value = true
  try {
    const group = await createGroup({ name: name.value, base_currency: currency.value })

    const validMembers = members.value.filter((m) => m.trim())
    for (const memberName of validMembers) {
      await addMember(group.id, memberName.trim())
    }

    router.push({ name: 'trip-detail', params: { id: group.id } })
  } finally {
    saving.value = false
  }
}
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/CreateGroup.vue frontend/src/composables/useCurrency.js
git commit -m "feat: CreateGroup view with name, currency, and participants form"
```

---

### Task 16: TripDetail View + ExpenseItem Component

**Files:**
- Create: `frontend/src/views/TripDetail.vue`
- Create: `frontend/src/components/ExpenseItem.vue`
- Create: `frontend/src/components/BalanceBar.vue`
- Create: `frontend/src/components/SettlementCard.vue`

- [ ] **Step 1: Create frontend/src/components/ExpenseItem.vue**

```vue
<template>
  <div class="border-b border-gray-100 py-3">
    <div class="flex justify-between">
      <div>
        <div class="font-semibold text-sm">{{ expense.title }}</div>
        <div class="text-gray-500 text-[11px] mt-0.5">
          {{ paidByName }} paid · {{ expense.split_type }}
        </div>
      </div>
      <div class="font-semibold text-sm">
        {{ formatAmount(expense.total_amount, expense.currency) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatAmount } from '../utils/format'

const props = defineProps({
  expense: Object,
  members: { type: Array, default: () => [] },
})

const paidByName = computed(() => {
  const m = props.members.find((m) => m.id === props.expense.paid_by_id)
  return m?.display_name || '?'
})
</script>
```

- [ ] **Step 2: Create frontend/src/components/BalanceBar.vue**

```vue
<template>
  <div class="mb-3">
    <div class="flex justify-between items-center mb-1">
      <div class="flex items-center gap-2">
        <div
          class="w-7 h-7 rounded-full text-white text-[10px] flex items-center justify-center font-semibold"
          :style="{ backgroundColor: color }"
        >
          {{ initials }}
        </div>
        <span class="font-medium text-sm">{{ balance.display_name }}</span>
      </div>
      <span
        class="font-semibold text-sm"
        :class="Number(balance.balance) >= 0 ? 'text-emerald-500' : 'text-red-500'"
      >
        {{ Number(balance.balance) >= 0 ? '+' : '' }}{{ formatAmount(balance.balance, currency) }}
      </span>
    </div>
    <div class="bg-gray-100 rounded-full h-2 overflow-hidden">
      <div
        class="h-full rounded-full"
        :class="Number(balance.balance) >= 0 ? 'bg-emerald-500' : 'bg-red-500'"
        :style="{ width: barWidth + '%', float: Number(balance.balance) < 0 ? 'right' : 'left' }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatAmount } from '../utils/format'

const props = defineProps({
  balance: Object,
  maxAbsBalance: Number,
  currency: String,
  color: String,
})

const initials = computed(() =>
  props.balance.display_name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase()
)

const barWidth = computed(() => {
  if (props.maxAbsBalance === 0) return 0
  return (Math.abs(Number(props.balance.balance)) / props.maxAbsBalance) * 100
})
</script>
```

- [ ] **Step 3: Create frontend/src/components/SettlementCard.vue**

```vue
<template>
  <div
    class="border rounded-xl p-3.5 mb-2.5"
    :class="settlement.is_settled && settlement.confirmed_by_to
      ? 'bg-emerald-50 border-emerald-200'
      : 'bg-white border-gray-200'"
  >
    <div class="flex items-center justify-center gap-3 mb-2.5">
      <div class="text-center">
        <div
          class="w-10 h-10 rounded-full text-white text-xs flex items-center justify-center mx-auto font-semibold"
          :style="{ backgroundColor: fromColor }"
        >
          {{ fromInitials }}
        </div>
        <div class="text-[11px] mt-1">{{ settlement.from_member_name }}</div>
      </div>
      <div class="text-center">
        <div class="font-bold text-base">{{ formatAmount(settlement.amount, settlement.currency) }}</div>
        <div class="text-gray-400 text-lg">→</div>
      </div>
      <div class="text-center">
        <div
          class="w-10 h-10 rounded-full text-white text-xs flex items-center justify-center mx-auto font-semibold"
          :style="{ backgroundColor: toColor }"
        >
          {{ toInitials }}
        </div>
        <div class="text-[11px] mt-1">{{ settlement.to_member_name }}</div>
      </div>
    </div>

    <div v-if="settlement.is_settled && settlement.confirmed_by_to" class="text-center text-xs text-emerald-600 font-medium">
      ✓ Paid and confirmed
    </div>
    <div v-else class="flex gap-2">
      <button
        @click="$emit('markPaid', settlement.id)"
        class="flex-1 py-2 rounded-lg text-xs font-semibold"
        :class="settlement.is_settled
          ? 'bg-emerald-500 text-white'
          : 'bg-emerald-500 text-white'"
      >
        {{ settlement.is_settled ? '✓ Paid' : '✓ Mark Paid' }}
      </button>
      <button
        @click="$emit('remind', settlement)"
        class="flex-1 bg-gray-100 py-2 rounded-lg text-xs text-gray-600 font-semibold"
      >
        Remind
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatAmount } from '../utils/format'

const props = defineProps({ settlement: Object })
defineEmits(['markPaid', 'remind'])

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase() }

const fromColor = computed(() => getColor(props.settlement.from_member_id))
const toColor = computed(() => getColor(props.settlement.to_member_id))
const fromInitials = computed(() => getInitials(props.settlement.from_member_name))
const toInitials = computed(() => getInitials(props.settlement.to_member_name))
</script>
```

- [ ] **Step 4: Create frontend/src/views/TripDetail.vue**

```vue
<template>
  <div class="min-h-screen pb-24">
    <!-- Header -->
    <div class="text-center pt-4 pb-2 px-4">
      <div class="font-bold text-lg">{{ group?.name }}</div>
      <div class="text-gray-500 text-xs">{{ group?.base_currency }}</div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 px-4 mb-3">
      <button
        v-for="t in ['expenses', 'balances', 'settlements']"
        :key="t"
        @click="tab = t"
        class="flex-1 py-2 rounded-lg text-xs font-semibold transition-colors"
        :class="tab === t ? 'bg-primary text-white' : 'bg-gray-100 text-gray-500'"
      >
        {{ t === 'expenses' ? 'Expenses' : t === 'balances' ? 'Balances' : 'Settlements' }}
      </button>
    </div>

    <!-- Expenses tab -->
    <div v-if="tab === 'expenses'" class="px-4">
      <ExpenseItem
        v-for="expense in expenses"
        :key="expense.id"
        :expense="expense"
        :members="group?.members || []"
      />
      <div v-if="expenses.length === 0" class="text-center text-gray-400 py-12 text-sm">
        No expenses yet
      </div>
    </div>

    <!-- Balances tab -->
    <div v-if="tab === 'balances'" class="px-4">
      <div class="text-center mb-4">
        <div class="text-[11px] text-gray-500 uppercase tracking-wide">Total Spending</div>
        <div class="text-2xl font-bold">{{ formatAmount(totalSpending, group?.base_currency) }}</div>
      </div>
      <BalanceBar
        v-for="(b, i) in balances"
        :key="b.member_id"
        :balance="b"
        :max-abs-balance="maxAbsBalance"
        :currency="group?.base_currency"
        :color="memberColor(b.member_id)"
      />
    </div>

    <!-- Settlements tab -->
    <div v-if="tab === 'settlements'" class="px-4">
      <SettlementCard
        v-for="s in settlements"
        :key="s.id"
        :settlement="s"
        @mark-paid="handleMarkPaid"
      />
      <div v-if="settlements.length === 0" class="text-center text-gray-400 py-12 text-sm">
        All settled!
      </div>
    </div>

    <!-- Bottom buttons -->
    <div class="fixed bottom-4 left-4 right-4 flex gap-2">
      <router-link
        :to="{ name: 'scan-receipt', params: { id: groupId } }"
        class="flex-1 bg-primary text-white py-3 rounded-xl text-center text-sm font-semibold no-underline"
      >
        📷 Scan Receipt
      </router-link>
      <router-link
        :to="{ name: 'add-expense', params: { id: groupId } }"
        class="flex-1 bg-gray-100 py-3 rounded-xl text-center text-sm font-semibold no-underline"
      >
        ✏️ Manual
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { fetchExpenses } from '../api/expenses'
import { fetchBalances, fetchSettlements, updateSettlement } from '../api/settlements'
import { formatAmount } from '../utils/format'
import ExpenseItem from '../components/ExpenseItem.vue'
import BalanceBar from '../components/BalanceBar.vue'
import SettlementCard from '../components/SettlementCard.vue'

const route = useRoute()
const store = useGroupsStore()
const groupId = Number(route.params.id)

const tab = ref('expenses')
const expenses = ref([])
const balances = ref([])
const settlements = ref([])

const group = computed(() => store.currentGroup)

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function memberColor(id) { return colors[id % colors.length] }

const totalSpending = computed(() =>
  expenses.value.reduce((sum, e) => sum + Number(e.total_amount), 0)
)

const maxAbsBalance = computed(() =>
  Math.max(...balances.value.map((b) => Math.abs(Number(b.balance))), 1)
)

async function handleMarkPaid(settlementId) {
  await updateSettlement(settlementId, { is_settled: true })
  settlements.value = await fetchSettlements(groupId)
}

onMounted(async () => {
  await store.loadGroup(groupId)
  expenses.value = await fetchExpenses(groupId)
  balances.value = await fetchBalances(groupId)
  settlements.value = await fetchSettlements(groupId)
})
</script>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/TripDetail.vue frontend/src/components/ExpenseItem.vue frontend/src/components/BalanceBar.vue frontend/src/components/SettlementCard.vue
git commit -m "feat: TripDetail view with expenses, balances, and settlements tabs"
```

---

### Task 17: AddExpense View

**Files:**
- Create: `frontend/src/views/AddExpense.vue`

- [ ] **Step 1: Create frontend/src/views/AddExpense.vue**

```vue
<template>
  <div class="min-h-screen px-4 pt-4">
    <h1 class="text-xl font-bold mb-4">Add Expense</h1>

    <form @submit.prevent="submit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
        <input v-model="title" type="text" placeholder="e.g. Restaurant" required
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary" />
      </div>

      <div class="flex gap-3">
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Amount</label>
          <input v-model="amount" type="number" step="0.01" min="0" required
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary" />
        </div>
        <div class="w-24">
          <label class="block text-sm font-medium text-gray-700 mb-1">Currency</label>
          <select v-model="currency"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none">
            <option v-for="c in CURRENCIES" :key="c.code" :value="c.code">{{ c.code }}</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Paid by</label>
        <select v-model="paidById" required
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none">
          <option v-for="m in members" :key="m.id" :value="m.id">{{ m.display_name }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Split mode</label>
        <div class="flex gap-2">
          <button type="button" v-for="mode in ['equal', 'custom']" :key="mode"
            @click="splitType = mode"
            class="flex-1 py-2 rounded-lg text-xs font-semibold border"
            :class="splitType === mode ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-300'">
            {{ mode === 'equal' ? 'Equal' : 'Custom' }}
          </button>
        </div>
      </div>

      <!-- Equal: select participants -->
      <div v-if="splitType === 'equal'">
        <label class="block text-sm font-medium text-gray-700 mb-1">Split among</label>
        <div class="space-y-2">
          <label v-for="m in members" :key="m.id" class="flex items-center gap-2 text-sm">
            <input type="checkbox" :value="m.id" v-model="splitAmong"
              class="rounded border-gray-300 text-primary focus:ring-primary" />
            {{ m.display_name }}
          </label>
        </div>
      </div>

      <!-- Custom: enter amounts -->
      <div v-if="splitType === 'custom'">
        <label class="block text-sm font-medium text-gray-700 mb-1">Amounts</label>
        <div class="space-y-2">
          <div v-for="m in members" :key="m.id" class="flex items-center gap-2">
            <span class="text-sm w-24 truncate">{{ m.display_name }}</span>
            <input v-model="customAmounts[m.id]" type="number" step="0.01" min="0" placeholder="0"
              class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none" />
          </div>
        </div>
        <!-- Smart validation indicator -->
        <div class="mt-2 text-xs" :class="remainderColor">
          Assigned: {{ assignedTotal }} / {{ amount || 0 }} · Remaining: {{ remainder }}
        </div>
        <button v-if="Number(remainder) > 0" type="button" @click="splitRemainder"
          class="mt-1 text-primary text-xs font-medium">
          Split remainder equally
        </button>
      </div>

      <button type="submit" :disabled="saving"
        class="w-full bg-primary text-white py-3 rounded-xl font-semibold text-sm disabled:opacity-50">
        {{ saving ? 'Saving...' : 'Save Expense' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { createExpense } from '../api/expenses'
import { useCurrency } from '../composables/useCurrency'

const route = useRoute()
const router = useRouter()
const store = useGroupsStore()
const { CURRENCIES } = useCurrency()

const groupId = Number(route.params.id)
const members = computed(() => store.currentGroup?.members || [])

const title = ref('')
const amount = ref('')
const currency = ref('')
const paidById = ref(null)
const splitType = ref('equal')
const splitAmong = ref([])
const customAmounts = reactive({})
const saving = ref(false)

const assignedTotal = computed(() =>
  Object.values(customAmounts).reduce((sum, v) => sum + (Number(v) || 0), 0).toFixed(2)
)
const remainder = computed(() => ((Number(amount.value) || 0) - Number(assignedTotal.value)).toFixed(2))
const remainderColor = computed(() =>
  Number(remainder.value) === 0 ? 'text-emerald-600' : Number(remainder.value) > 0 ? 'text-amber-600' : 'text-red-500'
)

function splitRemainder() {
  const remaining = Number(remainder.value)
  const unassigned = members.value.filter((m) => !customAmounts[m.id] || Number(customAmounts[m.id]) === 0)
  if (unassigned.length === 0) return
  const each = (remaining / unassigned.length).toFixed(2)
  unassigned.forEach((m) => { customAmounts[m.id] = each })
}

async function submit() {
  saving.value = true
  try {
    const payload = {
      title: title.value,
      total_amount: amount.value,
      currency: currency.value,
      paid_by_id: paidById.value,
      split_type: splitType.value,
    }
    if (splitType.value === 'equal') {
      payload.split_among = splitAmong.value
    } else if (splitType.value === 'custom') {
      payload.shares = Object.entries(customAmounts)
        .filter(([, v]) => Number(v) > 0)
        .map(([memberId, amt]) => ({ member_id: Number(memberId), amount: amt }))
    }
    await createExpense(groupId, payload)
    router.back()
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  if (!store.currentGroup) await store.loadGroup(groupId)
  currency.value = store.currentGroup?.base_currency || 'KZT'
  members.value.forEach((m) => splitAmong.value.push(m.id))
})
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/AddExpense.vue
git commit -m "feat: AddExpense view with equal/custom split modes and smart validation"
```

---

### Task 18: ScanReceipt View (All-in-One Assignment)

**Files:**
- Create: `frontend/src/views/ScanReceipt.vue`
- Create: `frontend/src/components/ReceiptItemRow.vue`
- Create: `frontend/src/components/ParticipantPicker.vue`
- Create: `frontend/src/components/ParticipantBar.vue`

- [ ] **Step 1: Create frontend/src/components/ParticipantPicker.vue**

```vue
<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-end justify-center bg-black/30" @click.self="$emit('close')">
    <div class="bg-white w-full max-w-md rounded-t-2xl p-4 pb-8">
      <div class="text-sm font-semibold mb-3">Who had this item?</div>
      <div class="space-y-2">
        <label
          v-for="m in members"
          :key="m.id"
          class="flex items-center gap-3 p-2 rounded-lg active:bg-gray-50"
        >
          <input
            type="checkbox"
            :value="m.id"
            v-model="selected"
            class="rounded border-gray-300 text-primary focus:ring-primary w-5 h-5"
          />
          <div
            class="w-8 h-8 rounded-full text-white text-xs flex items-center justify-center font-semibold"
            :style="{ backgroundColor: getColor(m.id) }"
          >
            {{ getInitials(m.display_name) }}
          </div>
          <span class="text-sm">{{ m.display_name }}</span>
        </label>
      </div>
      <button
        @click="$emit('assign', [...selected]); $emit('close')"
        class="w-full mt-4 bg-primary text-white py-3 rounded-xl font-semibold text-sm"
      >
        Done
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: Boolean,
  members: Array,
  currentAssignees: { type: Array, default: () => [] },
})
defineEmits(['assign', 'close'])

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() }

const selected = ref([])
watch(() => props.currentAssignees, (v) => { selected.value = [...v] }, { immediate: true })
</script>
```

- [ ] **Step 2: Create frontend/src/components/ParticipantBar.vue**

```vue
<template>
  <div class="flex gap-1.5 items-center p-2 bg-gray-50 rounded-xl">
    <div
      v-for="m in members"
      :key="m.id"
      class="w-9 h-9 rounded-full text-white text-[11px] flex items-center justify-center font-semibold cursor-pointer transition-all"
      :class="activeBrush === m.id ? 'ring-2 ring-offset-2 ring-primary scale-110' : ''"
      :style="{ backgroundColor: getColor(m.id) }"
      @click="$emit('brushTap', m.id)"
      @touchstart.prevent="startLongPress(m.id)"
      @touchend="cancelLongPress"
      @touchcancel="cancelLongPress"
    >
      {{ getInitials(m.display_name) }}
    </div>
    <div class="flex-1" />
    <div v-if="activeBrush" class="text-[10px] text-gray-500">
      Tap items to assign · <button @click="$emit('clearBrush')" class="text-primary font-medium">Done</button>
    </div>
    <div v-else class="text-[10px] text-gray-400">Hold = brush</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  members: Array,
  activeBrush: { type: Number, default: null },
})
defineEmits(['brushTap', 'clearBrush', 'activateBrush'])

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() }

const emit = defineEmits(['brushTap', 'clearBrush', 'activateBrush'])

let longPressTimer = null

function startLongPress(memberId) {
  longPressTimer = setTimeout(() => {
    emit('activateBrush', memberId)
  }, 500)
}

function cancelLongPress() {
  clearTimeout(longPressTimer)
}
</script>
```

- [ ] **Step 3: Create frontend/src/components/ReceiptItemRow.vue**

```vue
<template>
  <div
    class="rounded-lg p-2.5 mb-1.5 cursor-pointer active:opacity-80 transition-colors"
    :class="assignees.length > 0 ? 'bg-emerald-50 border border-emerald-200' : 'bg-amber-50 border border-amber-200'"
    @click="$emit('tap', item.index)"
  >
    <div class="flex justify-between items-center">
      <div>
        <div class="font-medium text-sm">{{ item.name }}</div>
        <div v-if="item.quantity > 1" class="text-gray-500 text-[11px]">× {{ item.quantity }}</div>
      </div>
      <div class="flex items-center gap-1.5">
        <div class="flex -space-x-1">
          <div
            v-for="memberId in assignees"
            :key="memberId"
            class="w-[22px] h-[22px] rounded-full border-2 border-white text-white text-[9px] flex items-center justify-center"
            :style="{ backgroundColor: getColor(memberId) }"
          >
            {{ getMemberInitials(memberId) }}
          </div>
          <div
            v-if="assignees.length === 0"
            class="w-[22px] h-[22px] rounded-full bg-gray-200 text-gray-400 text-sm flex items-center justify-center"
          >?</div>
        </div>
        <div class="font-semibold text-xs">{{ formatAmount(itemTotal, currency) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatAmount } from '../utils/format'

const props = defineProps({
  item: Object,
  assignees: { type: Array, default: () => [] },
  members: Array,
  currency: String,
})
defineEmits(['tap'])

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }

function getMemberInitials(id) {
  const m = props.members.find(m => m.id === id)
  if (!m) return '?'
  return m.display_name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

const itemTotal = computed(() => Number(props.item.price) * props.item.quantity)
</script>
```

- [ ] **Step 4: Create frontend/src/views/ScanReceipt.vue**

```vue
<template>
  <div class="min-h-screen px-4 pt-4 pb-24">
    <!-- Camera / Upload step -->
    <div v-if="!scannedItems.length && !scanning">
      <h1 class="text-xl font-bold mb-4">Scan Receipt</h1>
      <div
        class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer active:bg-gray-50"
        @click="$refs.fileInput.click()"
      >
        <div class="text-4xl mb-2">📷</div>
        <div class="text-gray-500 text-sm">Tap to take a photo or choose from gallery</div>
      </div>
      <input ref="fileInput" type="file" accept="image/*" capture="environment" class="hidden" @change="handleFile" />
    </div>

    <!-- Scanning indicator -->
    <div v-if="scanning" class="text-center py-16">
      <div class="text-3xl mb-3">🔍</div>
      <div class="text-gray-500 text-sm">Scanning receipt...</div>
    </div>

    <!-- All-in-one assignment screen -->
    <div v-if="scannedItems.length && !scanning">
      <div class="mb-3">
        <input v-model="expenseTitle" type="text" placeholder="Expense title"
          class="w-full font-semibold text-base border-0 border-b border-gray-200 pb-1 outline-none" />
        <div class="flex justify-between items-center mt-1">
          <div class="text-gray-500 text-[11px]">Paid by:</div>
          <select v-model="paidById" class="text-xs border border-gray-300 rounded px-2 py-1 outline-none">
            <option v-for="m in members" :key="m.id" :value="m.id">{{ m.display_name }}</option>
          </select>
        </div>
      </div>

      <!-- Items list -->
      <ReceiptItemRow
        v-for="(item, i) in scannedItems"
        :key="i"
        :item="{ ...item, index: i }"
        :assignees="assignments[i] || []"
        :members="members"
        :currency="currency"
        @tap="handleItemTap(i)"
      />

      <!-- Progress bar -->
      <div class="mt-3">
        <div class="bg-gray-100 rounded-full h-1.5 overflow-hidden">
          <div class="bg-emerald-500 h-full rounded-full transition-all" :style="{ width: assignedPercent + '%' }" />
        </div>
        <div class="flex justify-between text-[11px] text-gray-500 mt-1">
          <span>Assigned: {{ formatAmount(assignedTotal, currency) }}</span>
          <span>Remaining: {{ formatAmount(remainingTotal, currency) }}</span>
        </div>
      </div>

      <!-- Participant bar -->
      <div class="mt-3">
        <ParticipantBar
          :members="members"
          :active-brush="activeBrush"
          @brush-tap="handleBrushTap"
          @clear-brush="activeBrush = null"
        />
      </div>

      <!-- Save -->
      <button
        @click="saveExpense"
        :disabled="saving"
        class="w-full mt-4 bg-primary text-white py-3 rounded-xl font-semibold text-sm disabled:opacity-50"
      >
        {{ saving ? 'Saving...' : 'Save Expense' }}
      </button>
    </div>

    <!-- Participant Picker popup -->
    <ParticipantPicker
      :visible="pickerVisible"
      :members="members"
      :current-assignees="pickerCurrentAssignees"
      @assign="handlePickerAssign"
      @close="pickerVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { scanReceipt } from '../api/receipts'
import { createExpense } from '../api/expenses'
import { formatAmount } from '../utils/format'
import ReceiptItemRow from '../components/ReceiptItemRow.vue'
import ParticipantPicker from '../components/ParticipantPicker.vue'
import ParticipantBar from '../components/ParticipantBar.vue'

const route = useRoute()
const router = useRouter()
const store = useGroupsStore()
const groupId = Number(route.params.id)

const members = computed(() => store.currentGroup?.members || [])
const currency = computed(() => store.currentGroup?.base_currency || 'KZT')

const scanning = ref(false)
const saving = ref(false)
const scannedItems = ref([])
const assignments = reactive({})  // { itemIndex: [memberId, ...] }
const expenseTitle = ref('')
const paidById = ref(null)
const activeBrush = ref(null)

// Picker state
const pickerVisible = ref(false)
const pickerItemIndex = ref(null)
const pickerCurrentAssignees = computed(() => assignments[pickerItemIndex.value] || [])

// Totals
const receiptTotal = computed(() =>
  scannedItems.value.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0)
)
const assignedTotal = computed(() => {
  let total = 0
  for (const [idx, memberIds] of Object.entries(assignments)) {
    if (memberIds.length > 0) {
      const item = scannedItems.value[idx]
      total += Number(item.price) * item.quantity
    }
  }
  return total
})
const remainingTotal = computed(() => receiptTotal.value - assignedTotal.value)
const assignedPercent = computed(() =>
  receiptTotal.value > 0 ? (assignedTotal.value / receiptTotal.value) * 100 : 0
)

async function handleFile(event) {
  const file = event.target.files[0]
  if (!file) return
  scanning.value = true
  try {
    const result = await scanReceipt(file)
    scannedItems.value = result.items
    expenseTitle.value = 'Scanned receipt'
    // Init empty assignments
    result.items.forEach((_, i) => { assignments[i] = [] })
  } finally {
    scanning.value = false
  }
}

function handleItemTap(index) {
  if (activeBrush.value !== null) {
    // Brush mode: toggle this member on the item
    const memberId = activeBrush.value
    const current = assignments[index] || []
    if (current.includes(memberId)) {
      assignments[index] = current.filter((id) => id !== memberId)
    } else {
      assignments[index] = [...current, memberId]
    }
  } else {
    // Default mode: open picker
    pickerItemIndex.value = index
    pickerVisible.value = true
  }
}

function handlePickerAssign(memberIds) {
  assignments[pickerItemIndex.value] = memberIds
}

function handleBrushTap(memberId) {
  activeBrush.value = activeBrush.value === memberId ? null : memberId
}

async function saveExpense() {
  saving.value = true
  try {
    // Build items and shares
    const items = scannedItems.value.map((item, i) => ({
      name: item.name,
      price: String(item.price),
      quantity: item.quantity,
    }))

    // Calculate shares: for each item, split cost among assigned members
    const shares = []
    scannedItems.value.forEach((item, i) => {
      const memberIds = assignments[i] || []
      if (memberIds.length === 0) return
      const itemTotal = Number(item.price) * item.quantity
      const perPerson = (itemTotal / memberIds.length).toFixed(2)
      memberIds.forEach((memberId) => {
        shares.push({ member_id: memberId, amount: perPerson })
      })
    })

    await createExpense(groupId, {
      title: expenseTitle.value,
      total_amount: String(receiptTotal.value),
      currency: currency.value,
      paid_by_id: paidById.value,
      split_type: 'by_items',
      items,
      shares,
    })
    router.back()
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  if (!store.currentGroup) await store.loadGroup(groupId)
  if (members.value.length > 0) paidById.value = members.value[0].id
})
</script>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/ScanReceipt.vue frontend/src/components/ReceiptItemRow.vue frontend/src/components/ParticipantPicker.vue frontend/src/components/ParticipantBar.vue
git commit -m "feat: ScanReceipt view with camera, OCR, all-in-one assignment, brush mode"
```

---

### Task 19: GroupSettings View

**Files:**
- Create: `frontend/src/views/GroupSettings.vue`

- [ ] **Step 1: Create frontend/src/views/GroupSettings.vue**

```vue
<template>
  <div class="min-h-screen px-4 pt-4">
    <h1 class="text-xl font-bold mb-4">Group Settings</h1>

    <div v-if="group" class="space-y-6">
      <!-- Group name -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Trip name</label>
        <input v-model="groupName" type="text"
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary"
          @blur="updateName" />
      </div>

      <!-- Invite link -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Invite link</label>
        <div class="flex items-center gap-2">
          <input :value="inviteUrl" readonly
            class="flex-1 border border-gray-300 rounded-lg px-3 py-2.5 text-sm bg-gray-50 outline-none" />
          <button @click="copyInvite" class="bg-primary text-white px-4 py-2.5 rounded-lg text-sm font-semibold">
            Copy
          </button>
        </div>
      </div>

      <!-- Members -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Participants ({{ group.members.length }})
        </label>
        <div class="space-y-2">
          <div v-for="m in group.members" :key="m.id"
            class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
            <div class="w-8 h-8 rounded-full text-white text-xs flex items-center justify-center font-semibold"
              :style="{ backgroundColor: getColor(m.id) }">
              {{ getInitials(m.display_name) }}
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium">{{ m.display_name }}</div>
              <div class="text-[11px] text-gray-400">
                {{ m.user_id ? 'Telegram linked' : 'Virtual' }}
                {{ m.role === 'admin' ? ' · Admin' : '' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Add member -->
        <div class="flex gap-2 mt-2">
          <input v-model="newMemberName" type="text" placeholder="Add participant"
            class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none" />
          <button @click="handleAddMember" :disabled="!newMemberName.trim()"
            class="bg-primary text-white px-4 py-2 rounded-lg text-sm font-semibold disabled:opacity-50">
            Add
          </button>
        </div>
      </div>

      <!-- Archive / Delete -->
      <div class="pt-4 border-t border-gray-200">
        <button
          v-if="group.status === 'active'"
          @click="handleArchive"
          class="w-full py-3 border border-gray-300 rounded-xl text-sm font-semibold text-gray-600"
        >
          Archive Trip
        </button>
        <button
          v-else
          @click="handleUnarchive"
          class="w-full py-3 border border-primary rounded-xl text-sm font-semibold text-primary"
        >
          Reactivate Trip
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { updateGroup, addMember } from '../api/groups'
import { useTelegram } from '../composables/useTelegram'

const route = useRoute()
const router = useRouter()
const store = useGroupsStore()
const { showAlert } = useTelegram()
const groupId = Number(route.params.id)

const group = computed(() => store.currentGroup)
const groupName = ref('')
const newMemberName = ref('')

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() }

const inviteUrl = computed(() => {
  if (!group.value) return ''
  return `https://t.me/SplitCheckBot?startapp=${group.value.invite_code}`
})

function copyInvite() {
  navigator.clipboard.writeText(inviteUrl.value)
  showAlert('Invite link copied!')
}

async function updateName() {
  if (groupName.value !== group.value.name) {
    await updateGroup(groupId, { name: groupName.value })
    await store.loadGroup(groupId)
  }
}

async function handleAddMember() {
  await addMember(groupId, newMemberName.value.trim())
  newMemberName.value = ''
  await store.loadGroup(groupId)
}

async function handleArchive() {
  await updateGroup(groupId, { status: 'archived' })
  router.push({ name: 'my-trips' })
}

async function handleUnarchive() {
  await updateGroup(groupId, { status: 'active' })
  await store.loadGroup(groupId)
}

onMounted(async () => {
  if (!store.currentGroup) await store.loadGroup(groupId)
  groupName.value = group.value?.name || ''
})
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/GroupSettings.vue
git commit -m "feat: GroupSettings view with members, invite link, archive"
```

---

## Phase 6: Deployment

### Task 20: Docker Setup

**Files:**
- Create: `backend/Dockerfile`
- Create: `docker-compose.yml`
- Modify: `backend/app/main.py` — serve frontend static files in production

- [ ] **Step 1: Create backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create docker-compose.yml**

```yaml
version: "3.8"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: splitcheck
      POSTGRES_PASSWORD: splitcheck_dev
      POSTGRES_DB: splitcheck
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db

volumes:
  pgdata:
```

- [ ] **Step 3: Add static file serving to backend/app/main.py**

Add at the end of `main.py`, after all router includes:

```python
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Serve frontend in production
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
```

- [ ] **Step 4: Commit**

```bash
git add backend/Dockerfile docker-compose.yml backend/app/main.py
git commit -m "feat: Docker setup with PostgreSQL and production static file serving"
```

---

### Task 21: Final Integration Verification

- [ ] **Step 1: Start backend and database**

Run: `docker-compose up -d db && cd backend && alembic upgrade head && uvicorn app.main:app --reload --port 8000`

- [ ] **Step 2: Start frontend dev server**

Run: `cd frontend && npm run dev`

- [ ] **Step 3: Run all backend tests**

Run: `cd backend && python -m pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 4: Build frontend for production**

Run: `cd frontend && npm run build`
Expected: `dist/` directory created successfully.

- [ ] **Step 5: Commit any remaining changes**

```bash
git add -A
git commit -m "chore: final integration verification"
```

---

### Task 22: Cloudflare R2 Image Upload

**Files:**
- Create: `backend/app/services/storage.py`
- Modify: `backend/app/api/receipts.py` — save to R2 before scanning

- [ ] **Step 1: Create backend/app/services/storage.py**

```python
import uuid

import boto3
from botocore.config import Config

from app.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(signature_version="s3v4"),
    )


def upload_receipt_image(image_bytes: bytes, content_type: str) -> str:
    """Upload receipt image to R2 and return public URL."""
    ext = content_type.split("/")[-1]
    if ext == "jpeg":
        ext = "jpg"
    key = f"receipts/{uuid.uuid4().hex}.{ext}"

    client = get_s3_client()
    client.put_object(
        Bucket=settings.r2_bucket,
        Key=key,
        Body=image_bytes,
        ContentType=content_type,
    )

    return f"{settings.r2_endpoint}/{settings.r2_bucket}/{key}"
```

- [ ] **Step 2: Update backend/app/api/receipts.py — save to R2**

Add import and update the endpoint:

```python
from app.services.storage import upload_receipt_image

@router.post("/scan", response_model=ReceiptScanResponse)
async def scan_receipt_endpoint(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type: {file.content_type}",
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image too large (max 10 MB)")

    # Upload to R2 (non-blocking is not critical for MVP)
    image_url = None
    try:
        image_url = upload_receipt_image(image_bytes, file.content_type)
    except Exception:
        pass  # R2 upload failure should not block scanning

    try:
        result = await scan_receipt(image_bytes, file.content_type)
        result.image_url = image_url
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse receipt: {e}")

    return result
```

Also add `image_url` to the schema — update `backend/app/schemas/receipt.py`:

```python
class ReceiptScanResponse(BaseModel):
    items: list[ReceiptItem]
    total: Decimal | None = None
    tax: Decimal | None = None
    tips: Decimal | None = None
    currency: str | None = None
    image_url: str | None = None
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/storage.py backend/app/api/receipts.py backend/app/schemas/receipt.py
git commit -m "feat: Cloudflare R2 upload for receipt images"
```

---

### Task 23: Telegram Bot Notifications

**Files:**
- Create: `backend/app/services/telegram_bot.py`
- Modify: `backend/app/api/settlements.py` — add remind endpoint

- [ ] **Step 1: Add python-telegram-bot to requirements.txt**

Append to `backend/requirements.txt`:

```
python-telegram-bot==21.12
```

Run: `cd backend && pip install python-telegram-bot==21.12`

- [ ] **Step 2: Create backend/app/services/telegram_bot.py**

```python
from telegram import Bot

from app.config import settings

_bot: Bot | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(token=settings.bot_token)
    return _bot


async def send_notification(telegram_id: int, message: str) -> bool:
    """Send a message to a Telegram user. Returns True on success."""
    try:
        bot = get_bot()
        await bot.send_message(chat_id=telegram_id, text=message, parse_mode="HTML")
        return True
    except Exception:
        return False


async def send_settle_reminder(
    debtor_telegram_id: int,
    debtor_name: str,
    creditor_name: str,
    amount: str,
    currency: str,
    group_name: str,
) -> bool:
    message = (
        f"💸 <b>Payment Reminder</b>\n\n"
        f"{debtor_name}, you owe <b>{amount} {currency}</b> to {creditor_name}\n"
        f"Group: {group_name}\n\n"
        f"Open SplitCheck to settle up!"
    )
    return await send_notification(debtor_telegram_id, message)


async def send_expense_notification(
    telegram_id: int,
    payer_name: str,
    expense_title: str,
    amount: str,
    currency: str,
    group_name: str,
) -> bool:
    message = (
        f"📝 <b>New Expense</b>\n\n"
        f"{payer_name} added <b>{expense_title}</b> — {amount} {currency}\n"
        f"Group: {group_name}"
    )
    return await send_notification(telegram_id, message)
```

- [ ] **Step 3: Add remind endpoint to backend/app/api/settlements.py**

Add this endpoint after `update_settlement`:

```python
from app.services.telegram_bot import send_settle_reminder
from app.models import User as UserModel


@router.post("/api/settlements/{settlement_id}/remind")
async def remind_settlement(
    settlement_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settlement = await db.get(Settlement, settlement_id)
    if settlement is None:
        raise HTTPException(status_code=404, detail="Settlement not found")

    await _verify_membership(settlement.group_id, user.id, db)

    # Get debtor's telegram_id
    from_member = await db.get(GroupMember, settlement.from_member_id)
    if from_member.user_id is None:
        raise HTTPException(status_code=400, detail="Member has no Telegram account")

    debtor_user = await db.get(UserModel, from_member.user_id)
    to_member = await db.get(GroupMember, settlement.to_member_id)
    group = await db.get(Group, settlement.group_id)

    sent = await send_settle_reminder(
        debtor_telegram_id=debtor_user.telegram_id,
        debtor_name=from_member.display_name,
        creditor_name=to_member.display_name,
        amount=str(settlement.amount),
        currency=settlement.currency,
        group_name=group.name,
    )

    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send notification")

    return {"status": "sent"}
```

- [ ] **Step 4: Wire remind button in frontend — update SettlementCard.vue emit handler**

In `frontend/src/views/TripDetail.vue`, add the remind handler:

```javascript
import { useTelegram } from '../composables/useTelegram'
import client from '../api/client'

const { showAlert } = useTelegram()

async function handleRemind(settlement) {
  try {
    await client.post(`/settlements/${settlement.id}/remind`)
    showAlert('Reminder sent!')
  } catch (e) {
    showAlert(e.response?.data?.detail || 'Failed to send reminder')
  }
}
```

And in the template, bind the emit:

```html
<SettlementCard
  ...
  @remind="handleRemind"
/>
```

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/app/services/telegram_bot.py backend/app/api/settlements.py frontend/src/views/TripDetail.vue
git commit -m "feat: Telegram bot notifications with settle reminder"
```

---

### Task 24: PATCH Expense Endpoint

**Files:**
- Modify: `backend/app/api/expenses.py`

- [ ] **Step 1: Add PATCH endpoint to backend/app/api/expenses.py**

Add after `get_expense`:

```python
from app.schemas.expense import ExpenseCreate  # reuse for update


@router.patch("/api/expenses/{expense_id}", response_model=ExpenseOut)
async def update_expense(
    expense_id: int,
    body: ExpenseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Expense)
        .where(Expense.id == expense_id)
        .options(selectinload(Expense.items), selectinload(Expense.shares))
    )
    expense = result.scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    await _verify_membership(expense.group_id, user.id, db)

    # Update fields
    expense.title = body.title
    expense.total_amount = body.total_amount
    expense.currency = body.currency
    expense.exchange_rate = body.exchange_rate
    expense.paid_by_id = body.paid_by_id
    expense.split_type = body.split_type
    expense.receipt_image_url = body.receipt_image_url

    # Delete old items and shares
    for item in expense.items:
        await db.delete(item)
    for share in expense.shares:
        await db.delete(share)
    await db.flush()

    # Recreate items and shares (same logic as create)
    if body.split_type == "equal" and body.split_among:
        share_amount = (body.total_amount / len(body.split_among)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        for member_id in body.split_among:
            db.add(ExpenseShare(expense_id=expense.id, member_id=member_id, amount=share_amount))

    elif body.split_type == "by_items" and body.items:
        for item_data in body.items:
            item = ExpenseItem(
                expense_id=expense.id, name=item_data.name,
                price=item_data.price, quantity=item_data.quantity,
            )
            db.add(item)
            await db.flush()
        if body.shares:
            for share_data in body.shares:
                db.add(ExpenseShare(
                    expense_id=expense.id, member_id=share_data.member_id,
                    amount=share_data.amount, item_id=share_data.item_id,
                ))

    elif body.split_type == "custom" and body.shares:
        for share_data in body.shares:
            db.add(ExpenseShare(
                expense_id=expense.id, member_id=share_data.member_id,
                amount=share_data.amount,
            ))

    await db.commit()

    result = await db.execute(
        select(Expense).where(Expense.id == expense.id)
        .options(selectinload(Expense.items), selectinload(Expense.shares))
    )
    return result.scalar_one()
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/expenses.py
git commit -m "feat: PATCH expense endpoint for editing existing expenses"
```
