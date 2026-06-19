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
