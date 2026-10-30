from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.models.test import TestStatus


class OptionCreate(BaseModel):
    label: str = Field(..., max_length=1)  # A, B, C, D
    option_text: str = Field(..., min_length=1, max_length=2000)
    is_correct: bool = False

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in ("A", "B", "C", "D"):
            raise ValueError("Option label must be A, B, C, or D")
        return v

    @field_validator("option_text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Option text cannot be empty")
        return v


class QuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=1, max_length=5000)
    marks: float = Field(default=1.0, ge=0)
    order_index: int = Field(default=0, ge=0)
    options: list[OptionCreate]

    @field_validator("question_text")
    @classmethod
    def validate_question_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Question text cannot be empty")
        return v

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: list[OptionCreate]) -> list[OptionCreate]:
        if len(v) != 4:
            raise ValueError("Each question must contain exactly 4 answer options (A, B, C, D)")

        labels = [opt.label for opt in v]
        if sorted(labels) != ["A", "B", "C", "D"]:
            raise ValueError("Options must have unique labels A, B, C, and D")

        correct_count = sum(1 for opt in v if opt.is_correct)
        if correct_count != 1:
            raise ValueError("Exactly one option must be designated as the correct answer")

        return v


class TestCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = Field(default=None, max_length=2000)
    instructions: Optional[str] = Field(default=None, max_length=4000)
    duration_minutes: int = Field(..., ge=1, le=600)
    questions: list[QuestionCreate]

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Examination title cannot be empty")
        return v

    @field_validator("questions")
    @classmethod
    def validate_questions(cls, v: list[QuestionCreate]) -> list[QuestionCreate]:
        if not v:
            raise ValueError("Examination must contain at least one question")
        return v


class TestUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    description: Optional[str] = Field(default=None, max_length=2000)
    instructions: Optional[str] = Field(default=None, max_length=4000)
    duration_minutes: Optional[int] = Field(default=None, ge=1, le=600)
    questions: Optional[list[QuestionCreate]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Examination title cannot be empty")
        return v

    @field_validator("questions")
    @classmethod
    def validate_questions(cls, v: Optional[list[QuestionCreate]]) -> Optional[list[QuestionCreate]]:
        if v is not None and not v:
            raise ValueError("Examination must contain at least one question")
        return v


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class OptionResponse(BaseModel):
    id: int
    label: str
    option_text: str
    is_correct: bool

    model_config = {"from_attributes": True}


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    marks: float
    order_index: int
    options: list[OptionResponse]

    model_config = {"from_attributes": True}


class TestListItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int
    total_marks: float
    status: TestStatus
    test_code: str
    created_at: datetime
    updated_at: datetime
    question_count: int
    attempt_count: int

    model_config = {"from_attributes": True}


class TestDetailResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    duration_minutes: int
    total_marks: float
    status: TestStatus
    test_code: str
    created_at: datetime
    updated_at: datetime
    created_by: int
    question_count: int
    attempt_count: int
    questions: list[QuestionResponse]

    model_config = {"from_attributes": True}


class TeacherStatsResponse(BaseModel):
    total_tests: int
    total_attempts: int
    active_tests: int
    recent_tests: list[TestListItemResponse]
