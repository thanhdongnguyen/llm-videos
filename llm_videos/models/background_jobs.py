from typing import List, Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import time


class Base(DeclarativeBase):
    pass

class BackgroundJobs(Base):
    __tablename__ = "background_jobs"

    id: Mapped[int] = mapped_column(name="id", primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(name="job_id", type_=String, nullable=False)
    video_id: Mapped[int] = mapped_column(name="video_id", type_=Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(name="user_id", type_=Integer, nullable=False)
    status: Mapped[str] = mapped_column(name="status", type_=String, nullable=False)
    created_at: Mapped[Optional[int]] = mapped_column(name="created_at", type_=Integer, nullable=True, default=time.time())
    updated_at: Mapped[Optional[int]] = mapped_column(name="updated_at", type_=Integer, nullable=True, default=time.time())

