from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PaymentInstrument(Base):
    __tablename__ = "payment_instruments"

    id: Mapped[int] = mapped_column(primary_key=True)

    instrument_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    instrument_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id"),
        index=True,
        nullable=False,
    )