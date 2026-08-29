from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AbuseClusterMember(Base):
    __tablename__ = "abuse_cluster_members"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    cluster_id: Mapped[int] = mapped_column(
        ForeignKey("abuse_clusters.id"),
        index=True,
        nullable=False,
    )

    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id"),
        index=True,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_cluster_transaction",
            "cluster_id",
            "transaction_id",
            unique=True,
        ),
    )