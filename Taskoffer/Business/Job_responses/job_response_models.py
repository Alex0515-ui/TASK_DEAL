from sqlalchemy import func, ForeignKey, Enum as SQLEnum, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from Core.config.database import Base
from Core.auth.user_models import User

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Business.Jobs.job_models import Job

# СТАТУС ЗАЯВКИ
class Response_status(Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"



# ТАБЛИЦА ЗАЯВКИ НА РАБОТУ
class JobResponse(Base):
    __tablename__ = "job_responses"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id : Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    worker_id : Mapped[int] = mapped_column(ForeignKey("users.id"))

    offered_price : Mapped[int] = mapped_column(nullable=True)
    cover_letter : Mapped[str] = mapped_column(nullable=True)
    status : Mapped[Response_status] = mapped_column(SQLEnum(Response_status), default=Response_status.PENDING)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job : Mapped["Job"] = relationship("Job", back_populates="responses")
    worker : Mapped["User"] = relationship("User")

    __table_args__ = (
        UniqueConstraint("job_id", "worker_id", name="uniq_job_worker_response"),
    )

    def __repr__(self):
        return f"Offer from: {self.worker_id}, for job: {self.job_id}"