from sqlalchemy import func, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from Core.config.database import Base

from datetime import datetime
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from Interactions.Payment.payment_models import Wallet
    from Interactions.Reviews.review_models import Review
    from Business.Jobs.job_models import Job

# ДВА ВИДА РОЛИ ПОЛЬЗОВАТЕЛЯ
class Role(str, Enum):
    CLIENT = "Client"
    WORKER = "Worker"

# ТАБЛИЦА ПОЛЬЗОВАТЕЛЯ
class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    name : Mapped[str] = mapped_column(nullable=False)
    email : Mapped[str] = mapped_column(index=True, nullable=False, unique=True)

    password_hash : Mapped[str] = mapped_column(nullable=False)
    phone_number : Mapped[str] = mapped_column(unique=True, nullable=False)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    role : Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.CLIENT, nullable=False)

    wallet : Mapped["Wallet"] = relationship(back_populates="user", uselist=False)


    rating : Mapped[float] = mapped_column(default=5.0)
    completed_task : Mapped[int] = mapped_column(default=0)

    tasks_created : Mapped[List["Job"]] = relationship("Job", foreign_keys="[Job.owner_id]", back_populates="owner") 
    tasks_assigned : Mapped[List["Job"]] = relationship("Job", foreign_keys="[Job.worker_id]", back_populates="worker") 

    given_reviews : Mapped[List["Review"]] = relationship("Review", foreign_keys="[Review.from_user_id]")
    received_reviews : Mapped[List["Review"]] = relationship("Review", foreign_keys="[Review.to_user_id]") 

    def __repr__(self):
        return f"{self.name}, {self.role}"