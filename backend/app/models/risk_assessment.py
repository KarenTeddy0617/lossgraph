from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)

    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id"),
        index=True,
        nullable=False,
    )

    ml_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    graph_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    behavior_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    final_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )