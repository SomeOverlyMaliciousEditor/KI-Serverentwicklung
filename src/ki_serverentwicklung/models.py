from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


ID_TYPE = BigInteger().with_variant(Integer, "sqlite")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ID_TYPE, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    ordered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="open")
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
