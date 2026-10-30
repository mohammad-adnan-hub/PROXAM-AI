from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Answer(SQLModel, table=True):
    __tablename__ = "answers"

    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: int = Field(foreign_key="attempts.id", index=True)
    question_id: int = Field(foreign_key="questions.id", index=True)
    selected_option_id: Optional[int] = Field(default=None, foreign_key="options.id")
    is_marked_for_review: bool = Field(default=False)
    saved_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
