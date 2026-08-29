
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


# =========================================================
# Incoming transaction
# =========================================================

class TransactionCreate(BaseModel):
    transaction_code: str

    merchant_id: int
    customer_id: int

    device_id: int
    ip_address_id: int
    address_id: int
    payment_instrument_id: int

    amount: Decimal
    status: str = "SUCCESS"

    refund_status: str | None = None
    chargeback: bool = False


# =========================================================
# Transaction response
# =========================================================

class TransactionResponse(BaseModel):
    id: int
    transaction_code: str

    customer_id: int
    merchant_id: int

    amount: Decimal
    status: str

    refund_status: str | None
    chargeback: bool

    created_at: datetime

    class Config:
        from_attributes = True

