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
