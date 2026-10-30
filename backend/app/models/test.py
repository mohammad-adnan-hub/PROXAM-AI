from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class TestStatus(str, Enum):
    draft = "draft"
    active = "active"
    closed = "closed"


class Test(SQLModel, table=True):
    __tablename__ = "tests"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=300)
    description: Optional[str] = Field(default=None, max_length=2000)
    instructions: Optional[str] = Field(default=None, max_length=4000)
    duration_minutes: int = Field(ge=1)
    total_marks: float = Field(ge=0)
    status: TestStatus = Field(default=TestStatus.active)
    test_code: str = Field(unique=True, index=True, max_length=20)
    created_by: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
