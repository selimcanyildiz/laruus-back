from datetime import date as _date
import uuid

from sqlalchemy import Date, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class CreditUsage(Base):
    """Bir kullanıcının belirli bir gündeki toplam kredi tüketimi.

    Composite primary key (user_id, usage_date) sayesinde her kullanıcı için
    her gün tek bir satır tutulur ve harcama buraya eklenir.
    """

    __tablename__ = "credit_usage"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    usage_date: Mapped[_date] = mapped_column(Date, primary_key=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
