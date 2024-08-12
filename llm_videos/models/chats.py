import time
from typing import List, Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Chats(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(name="id", primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(name="channel_id", type_=String, nullable=False)
    user_id: Mapped[int] = mapped_column(name="user_id", type_=Integer, nullable=False)
    video_id: Mapped[int] = mapped_column(name="video_id", type_=Integer, nullable=False)
    message: Mapped[str] = mapped_column(name="message", type_=String, nullable=False)
    type: Mapped[str] = mapped_column(name="type", type_=String, nullable=False)
    status: Mapped[str] = mapped_column(name="status", type_=String, nullable=True)
    created_at: Mapped[Optional[int]] = mapped_column(name="created_at", type_=Integer, nullable=True,
                                                      default=time.time())
    updated_at: Mapped[Optional[int]] = mapped_column(name="updated_at", type_=Integer, nullable=True,
                                                      default=time.time())
