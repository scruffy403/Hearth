from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class BudgetConfig(Base):
    __tablename__ = "budget_config"

    category_dashboard: Mapped[str] = mapped_column(
        String(255), primary_key=True, nullable=False
    )
    mode: Mapped[str] = mapped_column(
        String(50), nullable=False, default="manual"
    )  # 'manual' | 'ynab' | 'stable'
    monthly_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<BudgetConfig {self.category_dashboard} {self.mode} {self.monthly_amount}>"