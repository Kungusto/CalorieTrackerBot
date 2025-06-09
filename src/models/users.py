from sqlalchemy import Date, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from datetime import date, datetime
from src.database import Base


class UsersORM(Base):
    __tablename__ = "Users"

    user_id: Mapped[str] = mapped_column(primary_key=True)
    calories: Mapped[int]
    calories_limit: Mapped[int]
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now())