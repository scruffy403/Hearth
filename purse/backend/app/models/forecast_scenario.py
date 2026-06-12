from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class ForecastScenario(Base):
    __tablename__ = "forecast_scenarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    days_ahead: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    exclude_categories: Mapped[Optional[list]] = mapped_column(
        ARRAY(String), nullable=True
    )
    exclude_tx_ids: Mapped[Optional[list]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=True
    )
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<ForecastScenario {self.name} +{self.days_ahead}d>"