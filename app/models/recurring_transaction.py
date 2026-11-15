from sqlalchemy import (
    Integer,
    Float,
    Column,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    func,
)

from app.database import Base


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)

    purpose = Column(String, nullable=False)

    category = Column(String(100), nullable=True)

    frequency = Column(String, nullable=False)

    start_date = Column(Date, nullable=False)

    end_date = Column(Date, nullable=True)

    next_run_date = Column(Date, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
