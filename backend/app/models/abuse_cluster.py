from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    DateTime,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AbuseCluster(Base):
    __tablename__ = "abuse_clusters"

    id: Mapped[int] = mapped_column(primary_key=True)

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id"),
        index=True,
        nullable=False,
    )

    cluster_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    risk_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    member_count: Mapped[int] = mapped_column(
        nullable=False,
    )

    exposure_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )