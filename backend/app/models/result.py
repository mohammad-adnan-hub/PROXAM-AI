from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Result(SQLModel, table=True):
    __tablename__ = "results"

    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: int = Field(foreign_key="attempts.id", unique=True, index=True)
    score: float
    total_marks: float
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    percentage: float
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
