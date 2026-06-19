from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.currencies import router as currencies_router
from app.api.expenses import router as expenses_router
from app.api.groups import router as groups_router
from app.api.receipts import router as receipts_router
from app.api.settlements import router as settlements_router
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
app.include_router(groups_router)
app.include_router(expenses_router)
app.include_router(settlements_router)
app.include_router(receipts_router)
app.include_router(currencies_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Serve frontend in production
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
