
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReleaseRecord(Base):
    __tablename__ = "releases"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    version: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    git_commit: Mapped[str] = mapped_column(
        String(40), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="registered"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
