from sqlalchemy import func, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from Core.config.database import Base
from Business.Deals.deal_models import Deal
from Core.auth.user_models import User
from datetime import datetime 

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