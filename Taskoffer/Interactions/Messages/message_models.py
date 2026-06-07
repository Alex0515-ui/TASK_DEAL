from sqlalchemy import func, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from Core.config.database import Base
from Core.auth.user_models import User
from Business.Deals.deal_models import Deal
from datetime import datetime


# Таблица сообщения в чате
class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    sender_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    deal_id : Mapped[int] = mapped_column(ForeignKey("deals.id"), index=True)

    text : Mapped[str] = mapped_column(Text, nullable=False)

    read_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True) 
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sender : Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    deal : Mapped["Deal"] = relationship("Deal", foreign_keys=[deal_id])