from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Boolean,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    transaction_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id"),
        index=True,
        nullable=False,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
        nullable=False,
    )

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id"),
        index=True,
        nullable=False,
    )

    ip_address_id: Mapped[int] = mapped_column(
        ForeignKey("ip_addresses.id"),
        index=True,
        nullable=False,
    )

    address_id: Mapped[int] = mapped_column(
        ForeignKey("addresses.id"),
        index=True,
        nullable=False,
    )

    payment_instrument_id: Mapped[int] = mapped_column(
        ForeignKey("payment_instruments.id"),
        index=True,
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    refund_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    chargeback: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_abuse: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        index=True,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_transactions_merchant_created",
            "merchant_id",
            "created_at",
        ),
    )