from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id"),
        index=True,
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    transaction_id: Mapped[int | None] = mapped_column(
        ForeignKey("transactions.id"),
        nullable=True,
        index=True,
    )

    action: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )