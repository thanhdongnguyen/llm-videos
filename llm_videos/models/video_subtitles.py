from typing import List, Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class VideoSubtitles(Base):
    __tablename__ = "video_subtitles"

    id: Mapped[int] = mapped_column(name="id", primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(name="video_id", type_=Integer, nullable=False)
    language: Mapped[str] = mapped_column(name="language", type_=String, nullable=False)
    content: Mapped[str] = mapped_column(name="content", type_=String, nullable=False)
    created_at: Mapped[Optional[str]] = mapped_column(name="created_at", type_=Integer, nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(name="updated_at", type_=Integer, nullable=True)

