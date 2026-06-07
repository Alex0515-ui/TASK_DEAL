from sqlalchemy import func, ForeignKey, Enum as SQLEnum, DateTime, UniqueConstraint, CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from Core.config.database import Base
from Core.auth.user_models import User

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Business.Job_responses.job_response_models import JobResponse
    
# СТАТУС РАБОТЫ
class Job_status(Enum):
    IN_SEARCH = "In search"
    PENDING_SELECTION = "Pending selection"
    ACCEPTED = "Accepted"
    DONE = "Done"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"

# ТИП РАБОТЫ
class Job_type(Enum):
    ASSEMBLY = "Сборка" 
    MOUNTING = "Монтаж и установка"
    HANDYMAN = "Починка"
    CLEANING = "Уборка"
    MOVING = "Перевозка"
    ELECTRICAL = "Электричество"
    PLUMBING = "Сантехника"
    YARDWORK = "Дворовая работа"
    DELIVERY = "Доставка"
    REPAIR = "Ремонт"
    TECH = "Техника"


# ТАБЛИЦА РАБОТЫ
class Job(Base):
    __tablename__ = "jobs"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    title : Mapped[str] = mapped_column(nullable=False)
    description : Mapped[str] = mapped_column(nullable=False)

    price : Mapped[int] = mapped_column(nullable=False)

    owner_id : Mapped[int] = mapped_column(ForeignKey('users.id'))
    worker_id : Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True, default=None)
    owner : Mapped["User"] = relationship("User", foreign_keys=[owner_id], back_populates="tasks_created")
    worker : Mapped["User"] = relationship("User", foreign_keys=[worker_id], back_populates="tasks_assigned")


    status : Mapped[Job_status] = mapped_column(SQLEnum(Job_status), default=Job_status.IN_SEARCH, index=True)
    type : Mapped[Job_type] = mapped_column(SQLEnum(Job_type), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    deadline : Mapped[datetime] = mapped_column(DateTime(timezone=True))

    responses : Mapped[list["JobResponse"]] = relationship("JobResponse", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"{self.title}, {self.price}, {self.status}"