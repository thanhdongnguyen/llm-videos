from typing import List, Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class Videos(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(name="id", primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(name="title", type_=String, nullable=False)
    description: Mapped[str] = mapped_column(name="description", type_=String, nullable=False)
    video_url: Mapped[str] = mapped_column(name="video_url", type_=String, nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(name="thumbnail_url", type_=String, nullable=False)
    video_id: Mapped[str] = mapped_column(name="video_id", type_=String, nullable=False)
    lang: Mapped[str] = mapped_column(name="lang", type_=String, nullable=False)
    created_at: Mapped[Optional[str]] = mapped_column(name="created_at", type_=Integer, nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(name="updated_at", type_=Integer, nullable=True)

