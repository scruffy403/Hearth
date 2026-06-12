from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    ynab_transaction_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GBP")
    merchant_raw: Mapped[str] = mapped_column(Text, nullable=False)
    merchant_clean: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_ynab: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category_dashboard: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    category_source: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 'ynab' | 'ml' | 'manual_override'
    ml_confidence: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    ynab_approved: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_transfer: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<Transaction {self.date} {self.merchant_clean} {self.amount}>"
        )