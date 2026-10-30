from typing import Optional
from sqlmodel import Field, SQLModel


class Option(SQLModel, table=True):
    __tablename__ = "options"

    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="questions.id", index=True)
    option_text: str = Field(max_length=2000)
    label: str = Field(max_length=1)  # A, B, C, D
    is_correct: bool = Field(default=False)
