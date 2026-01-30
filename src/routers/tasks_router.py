from fastapi import APIRouter, Query, status, HTTPException, Depends
from typing import List, Optional, Annotated
from ..schemas.tasks import TaskResponse, TaskCreate, TaskUpdate, TaskStatus
from ..database import Task, User
# from ..dependencies import get_current_user, get_db
from ..messages import ErrorMsg, SuccessMsg
# from sqlalchemy.orm import Session
from .. import service
from sqlalchemy.orm import Session
from ..dependencies import get_current_user, get_db


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"detail": ErrorMsg.TASK_NOT_FOUND}},
)

# CurrentUser = Annotated[User, Depends(get_current_user)]
# DB = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: User = Depends(get_current_user),
):
    db_task = Task(**task.model_dump(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get(
    "/",
    response_model=List[TaskResponse],
    responses={404: {"description": ErrorMsg.TASK_NOT_FOUND}},
)
def read_task(
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[TaskStatus] = Query(None),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Task).filter(Task.user_id == current_user.id)

    if status:
        query = query.filter(Task.status == status)

    return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        403: {"description": ErrorMsg.TASK_FORBIDDEN},
        404: {"description": ErrorMsg.TASK_NOT_FOUND},
    },
)
def read_by_id_task(db: Annotated[Session, Depends(get_db)], task_id: int, current_user: User = Depends(get_current_user)):
    task = service.get_task_by_id(db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMsg.TASK_NOT_FOUND
        )

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMsg.TASK_FORBIDDEN,
        )

    return task


@router.patch(
    "/",
    response_model=TaskResponse,
    responses={
        403: {"description": ErrorMsg.TASK_FORBIDDEN},
        404: {"description": ErrorMsg.TASK_NOT_FOUND},
        422: {"description": ErrorMsg.INVALID_CREDENTIALS},
    },
)
def update_task(
    db: Annotated[Session, Depends(get_db)], task_id: int, task_update: TaskUpdate, current_user: User = Depends(get_current_user)
):
    task = service.get_task_by_id(db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMsg.TASK_NOT_FOUND
        )

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMsg.TASK_FORBIDDEN,
        )

    # Update just sent fields
    updated_task = service.update_task(db, task, task_update)

    return updated_task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": SuccessMsg.TASK_DELETED},
        403: {"description": ErrorMsg.TASK_FORBIDDEN},
        404: {"description": ErrorMsg.TASK_NOT_FOUND},
    },
)
def delete_by_id_task(
    db: Annotated[Session, Depends(get_db)],
    task_id: int,
    current_user: User = Depends(get_current_user),
):
    task = service.get_task_by_id(db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMsg.TASK_NOT_FOUND
        )

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMsg.TASK_FORBIDDEN,
        )

    service.delete_task(db, task)

    return None
