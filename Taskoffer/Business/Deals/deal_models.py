from sqlalchemy import func, ForeignKey, Enum as SQLEnum, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from Core.config.database import Base
from Core.auth.user_models import User
from Business.Jobs.job_models import Job
from datetime import datetime


# СТАТУСЫ СДЕЛКИ
class DealStatus(Enum):
    NEGOTIATION = "Negotiation"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


# ТАБЛИЦА СДЕЛОК
class Deal(Base):
    __tablename__ = "deals"

    # Ключи
    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id : Mapped[int] = mapped_column(ForeignKey('jobs.id'), unique=True)
    worker_id : Mapped[int] = mapped_column(ForeignKey('users.id'))
    client_id : Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Данные клиента и работника
    worker_email : Mapped[str] = mapped_column(nullable=False)
    client_email : Mapped[str] = mapped_column(nullable=False)

    worker_phone_number : Mapped[str] = mapped_column(nullable=False)
    client_phone_number : Mapped[str] = mapped_column(nullable=False)

    # Цена договоренная
    agreed_price : Mapped[int] = mapped_column(nullable=False)

    # Это сроки выполнения работы
    deadline : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status : Mapped[DealStatus] = mapped_column(SQLEnum(DealStatus), default=DealStatus.NEGOTIATION)

    # Подписи 
    worker_signed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),  nullable=True)   
    client_signed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),  nullable=True)
    is_fully_signed : Mapped[bool] = mapped_column(default=False)
    worker_completed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),  nullable=True)
    client_completed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),  nullable=True)

    # Времена
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Изменения
    cancel_reason : Mapped[str] = mapped_column(nullable=True)
    change_reason : Mapped[str] = mapped_column(nullable=True)
    last_action_by : Mapped[int] = mapped_column(nullable=True)
    
    # Для удобства связи
    worker : Mapped["User"] = relationship("User", foreign_keys=[worker_id])
    client : Mapped["User"] = relationship("User", foreign_keys=[client_id])
    job: Mapped["Job"] = relationship("Job", foreign_keys=[job_id])

    __table_args__ = (
        CheckConstraint("agreed_price > 0", name='check_price_positive'),
    )