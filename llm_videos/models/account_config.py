from typing import List, Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class AccountConfig(Base):
    __tablename__ = "account_config"

    user_id: Mapped[int] = mapped_column(name="user_id", type_=Integer, nullable=False, primary_key=True)
    target_language: Mapped[str] = mapped_column(name="target_language", type_=String, nullable=True)
    created_at: Mapped[Optional[int]] = mapped_column(name="created_at", type_=Integer, nullable=True)
    updated_at: Mapped[Optional[int]] = mapped_column(name="updated_at", type_=Integer, nullable=True)