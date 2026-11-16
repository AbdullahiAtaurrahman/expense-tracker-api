from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Date,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        UniqueConstraint(
            "recurring_transaction_id",
            "recurrence_date",
            name="uq_transaction_recurring_date",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    purpose = Column(String(200), nullable=False)

    recurring_transaction_id = Column(
        Integer,
        ForeignKey(
            "recurring_transactions.id",
            name="fk_transactions_recurring_transaction_id",
        ),
        nullable=True,
    )

    recurrence_date = Column(Date, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
