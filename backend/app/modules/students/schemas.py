from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.attempt import AttemptStatus
from app.models.test import TestStatus
from app.models.identity_verification import IdentityVerificationStatus


class TestCodeValidationRequest(BaseModel):
    test_code: str = Field(..., min_length=1, max_length=20)

    @field_validator("test_code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError("Test code cannot be empty")
        return v


class StudentTestValidationResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int
    total_marks: float
    question_count: int
    status: TestStatus
    test_code: str
    validation_token: str

    model_config = {"from_attributes": True}


class StudentTestDetailsResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int
    total_marks: float
    question_count: int
    status: TestStatus
    test_code: str

    model_config = {"from_attributes": True}


class AttemptResponse(BaseModel):
    id: int
    test_id: int
    student_id: int
    status: AttemptStatus
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    time_limit_ends_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    identity_verified: bool
    warning_count: int = 0

    model_config = {"from_attributes": True}


class AnswerSaveRequest(BaseModel):
    selected_option_id: Optional[int] = None
    is_marked_for_review: bool = False


class StudentAnswerResponse(BaseModel):
    id: int
    attempt_id: int
    question_id: int
    selected_option_id: Optional[int] = None
    is_marked_for_review: bool
    saved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StudentQuestionOptionResponse(BaseModel):
    id: int
    label: str
    option_text: str

    model_config = {"from_attributes": True}


class StudentQuestionResponse(BaseModel):
    id: int
    question_text: str
    marks: float
    order_index: int
    options: list[StudentQuestionOptionResponse]

    model_config = {"from_attributes": True}


class ResultResponse(BaseModel):
    status: AttemptStatus
    id: int
    attempt_id: int
    score: float
    total_marks: float
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    percentage: float
    calculated_at: datetime

    model_config = {"from_attributes": True}


class AttemptHistoryItem(BaseModel):
    id: int
    test_id: int
    test_title: str
    test_code: str
    status: AttemptStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    score: Optional[float] = None
    total_marks: Optional[float] = None
    percentage: Optional[float] = None
    correct_count: Optional[int] = None
    incorrect_count: Optional[int] = None
    unanswered_count: Optional[int] = None
    calculated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AttemptFinalizationResponse(BaseModel):
    id: int
    test_id: int
    student_id: int
    status: AttemptStatus
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    time_limit_ends_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    identity_verified: bool
    result: Optional[ResultResponse] = None

    model_config = {"from_attributes": True}


class IdentityVerificationStatusResponse(BaseModel):
    attempt_id: int
    status: IdentityVerificationStatus
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None
    can_start_examination: bool
    message: Optional[str] = None

    model_config = {"from_attributes": True}


class IdentityVerificationSubmitResponse(BaseModel):
    attempt_id: int
    status: IdentityVerificationStatus
    submitted_at: datetime
    can_start_examination: bool
    message: str

    model_config = {"from_attributes": True}



class TeacherAttemptListItem(BaseModel):
    attempt_id: int
    student_id: int
    student_name: str
    student_email: str
    status: AttemptStatus
    warning_count: int
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    identity_verified: bool = False
    proctoring_event_count: int = 0
    latest_event_timestamp: Optional[datetime] = None
    latest_event_type: Optional[str] = None
    latest_event_severity: Optional[str] = None

    model_config = {"from_attributes": True}


class TeacherAttemptDetail(BaseModel):
    attempt_id: int
    student_id: int
    student_name: str
    student_email: str
    test_id: int
    test_title: str
    status: AttemptStatus
    warning_count: int
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    identity_verified: bool = False
    identity_verification_status: Optional[str] = None
    proctoring_event_count: int = 0

    model_config = {"from_attributes": True}


class TeacherAttemptResult(BaseModel):
    attempt_id: int
    status: AttemptStatus
    score: Optional[float] = None
    total_marks: Optional[float] = None
    percentage: Optional[float] = None
    correct_count: Optional[int] = None
    incorrect_count: Optional[int] = None
    unanswered_count: Optional[int] = None
    calculated_at: Optional[datetime] = None
