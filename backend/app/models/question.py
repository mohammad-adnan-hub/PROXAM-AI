from typing import Optional
from sqlmodel import Field, SQLModel


class Question(SQLModel, table=True):
    __tablename__ = "questions"

    id: Optional[int] = Field(default=None, primary_key=True)
    test_id: int = Field(foreign_key="tests.id", index=True)
    question_text: str = Field(max_length=5000)
    marks: float = Field(default=1.0, ge=0)
    order_index: int = Field(default=0, ge=0)
