from typing import List, Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(name="user_id", primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(name="email", type_=String, nullable=False)
    password: Mapped[str] = mapped_column(name="password", type_=String, nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(name="avatar", type_=String, nullable=True)
    source_register: Mapped[Optional[str]] = mapped_column(name="source_register", type_=String, nullable=True)
    created_at: Mapped[Optional[int]] = mapped_column(name="created_at", type_=Integer, nullable=True)
    updated_at: Mapped[Optional[int]] = mapped_column(name="updated_at", type_=Integer, nullable=True)

