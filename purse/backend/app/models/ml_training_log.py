from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class MLTrainingLog(Base):
    __tablename__ = "ml_training_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    trained_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False)
    category_distribution: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True
    )
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<MLTrainingLog {self.trained_at} samples={self.sample_count}>"