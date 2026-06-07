from sqlalchemy import func, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from Core.config.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Core.auth.user_models import User

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