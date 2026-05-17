from sqlalchemy import func, ForeignKey, Enum as SQLEnum, DateTime, UniqueConstraint, CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from Core.config.database import Base
from datetime import datetime

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

    tasks_created : Mapped[list["Job"]] = relationship("Job", foreign_keys="[Job.owner_id]", back_populates="owner") 
    tasks_assigned : Mapped[list["Job"]] = relationship("Job", foreign_keys="[Job.worker_id]", back_populates="worker") 

    given_reviews : Mapped[list["Review"]] = relationship("Review", foreign_keys="[Review.from_user_id]")
    received_reviews : Mapped[list["Review"]] = relationship("Review", foreign_keys="[Review.to_user_id]") 

    def __repr__(self):
        return f"{self.name}, {self.role}"
    
# ========================================================================
# ================== ПЛАТЕЖНЫЕ ТАБЛИЦЫ ============================
# ============================================================================


# КОШЕЛЕК ПОЛЬЗОВАТЕЛЯ
class Wallet(Base):
    __tablename__ = "wallets"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user : Mapped["User"] = relationship(back_populates="wallet")
    balance : Mapped[float] = mapped_column(default=0)

    def __repr__(self):
        return f"{self.user_id}, {self.balance}"
    

# ТИПЫ ТРАНЗАКЦИЙ
class TransactionType(Enum):
    REFILL = "Пополнение"
    WITHDRAW = "Снятие"
    HOLD = "Заморозка"
    PAYOUT = "Выплата"
    REFUND = "Возврат"

# ТАБЛИЦА ТРАНЗАКЦИЙ
class Transaction(Base):
    __tablename__ = "transactions"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)

    type : Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType))
    
    wallet_id : Mapped[int] = mapped_column(ForeignKey("wallets.id"), index=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deals.id"), nullable=True)

    amount : Mapped[int] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


#====================================================================
# ============== JOB модели снизу ====================================
# =====================================================================

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

# СТАТУС ЗАЯВКИ
class Response_status(Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


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
    

# ==================================================================================
# =============================== DEALS (СДЕЛКИ) =======================================   
# ==================================================================================

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

    
 # ========================== ТАБЛИЦА ОТЗЫВОВ ==============================
 # ===========================================================================

 # Сущность отзыва
class Review(Base):
    __tablename__ = "reviews"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deals.id"))

    from_user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    to_user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))

    rating : Mapped[int] = mapped_column(nullable=False)
    comment : Mapped[str] = mapped_column(nullable=True)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    deal : Mapped["Deal"] = relationship("Deal", foreign_keys=[deal_id])

    from_user : Mapped["User"] = relationship("User", foreign_keys=[from_user_id], overlaps="given_reviews")
    to_user : Mapped["User"] = relationship("User", foreign_keys=[to_user_id], overlaps="received_reviews")

    __table_args__ = (
        UniqueConstraint("deal_id", "from_user_id", name="uniq_review_user"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

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