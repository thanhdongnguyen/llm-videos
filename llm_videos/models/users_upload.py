from typing import List, Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class UsersUpload(Base):
    __tablename__ = "users_upload"

    id: Mapped[int] = mapped_column(name="id", primary_key=True)
    video_id: Mapped[int] = mapped_column(name="video_id", type_=Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(name="user_id", type_=Integer, nullable=False)
    created_at: Mapped[Optional[str]] = mapped_column(name="created_at", type_=Integer, nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(name="updated_at", type_=Integer, nullable=True)

