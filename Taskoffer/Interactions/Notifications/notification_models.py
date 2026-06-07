from sqlalchemy import func, ForeignKey, Enum as SQLEnum, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from Core.config.database import Base
from Core.auth.user_models import User

from datetime import datetime

# С чем связано уведомление (Чат или работа)
class NotificationType(Enum):
    CHAT = "CHAT"
    JOB = "JOB"

# Уведомления в платформе
class Notification(Base):
    __tablename__ = "notifications"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    text: Mapped[str] = mapped_column(Text, nullable=False)

    type : Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType))

    related_id: Mapped[int] = mapped_column(nullable=True)

    is_read: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user : Mapped["User"] = relationship("User", foreign_keys=[user_id])