from typing import List, Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class Authentication(Base):
    __tablename__ = "authentication"

    id: Mapped[int] = mapped_column(name="id", primary_key=True)
    user_id: Mapped[int] = mapped_column(name="user_id", type_=Integer, nullable=False)
    device_id: Mapped[str] = mapped_column(name="device_id", type_=String, nullable=True)
    access_token: Mapped[str] = mapped_column(name="access_token", type_=String, nullable=False)
    expired_at: Mapped[int] = mapped_column(name="expired_at", type_=Integer, nullable=False)
    created_at: Mapped[Optional[int]] = mapped_column(name="created_at", type_=Integer, nullable=True)
    updated_at: Mapped[Optional[int]] = mapped_column(name="updated_at", type_=Integer, nullable=True)

