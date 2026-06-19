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
