from sqlalchemy import Column, Float, Integer, String

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    purpose = Column(String(200), nullable=False)
