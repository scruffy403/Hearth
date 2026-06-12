from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class MerchantOverride(Base):
    __tablename__ = "merchant_overrides"

    merchant_clean: Mapped[str] = mapped_column(
        String(255), primary_key=True, nullable=False
    )
    category_dashboard: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<MerchantOverride {self.merchant_clean} -> {self.category_dashboard}>"