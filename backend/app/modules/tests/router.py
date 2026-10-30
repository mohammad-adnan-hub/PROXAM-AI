from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.dependencies import get_db, require_teacher
from app.models.user import User
from app.modules.tests.schemas import (
    TestCreateRequest,
    TestUpdateRequest,
    TestListItemResponse,
    TestDetailResponse,
    TeacherStatsResponse,
)
from app.modules.tests import service

router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("/", response_model=TestDetailResponse, status_code=status.HTTP_201_CREATED)
def create_test(
    payload: TestCreateRequest,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> TestDetailResponse:
    """
    Create a new MCQ examination with questions and answer options.
    Automatically generates a unique test code and marks the examination active.
    """
    try:
        created = service.create_test(db, current_user.id, payload)
        return TestDetailResponse.model_validate(created)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/", response_model=list[TestListItemResponse])
def list_teacher_tests(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> list[TestListItemResponse]:
    """
    List all examinations created by the authenticated teacher.
    """
    tests = service.get_teacher_tests(db, current_user.id)
    return [TestListItemResponse.model_validate(t) for t in tests]


@router.get("/stats", response_model=TeacherStatsResponse)
def get_teacher_stats(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> TeacherStatsResponse:
    """
    Aggregate metrics and recent examinations for the teacher dashboard.
    """
    stats = service.get_teacher_stats(db, current_user.id)
    return TeacherStatsResponse.model_validate(stats)


@router.get("/{test_id}", response_model=TestDetailResponse)
def get_test_details(
    test_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> TestDetailResponse:
    """
    Get full examination details including questions and options for the test author.
    """
    test_data = service.get_test_by_id_for_teacher(db, test_id, current_user.id)
    if not test_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Examination not found or you do not have permission to view it.",
        )
    return TestDetailResponse.model_validate(test_data)


@router.put("/{test_id}", response_model=TestDetailResponse)
def update_test(
    test_id: int,
    payload: TestUpdateRequest,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> TestDetailResponse:
    """
    Update an examination. Modifying questions is only permitted if no candidate attempts exist.
    """
    try:
        updated = service.update_test(db, test_id, current_user.id, payload)
        return TestDetailResponse.model_validate(updated)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{test_id}")
def delete_test(
    test_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Safely delete an examination. Fails if any candidate attempts exist.
    """
    try:
        service.delete_test(db, test_id, current_user.id)
        return {"message": "Examination deleted successfully", "test_id": test_id}
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
