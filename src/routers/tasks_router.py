from fastapi import APIRouter, Query, status, HTTPException, Depends
from typing import List, Annotated
from ..schemas.tasks import TaskResponse, TaskCreate, TaskUpdate, TaskStatus
from ..database import Task, User
from ..messages import ErrorMsg, SuccessMsg
from .. import service
from sqlalchemy.orm import Session
from ..dependencies import get_current_user, get_db


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"detail": ErrorMsg.TASK_NOT_FOUND}},
)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
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
def read_tasks(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    status: Annotated[TaskStatus | None, Query()] = None,
):
    query = db.query(Task).filter(Task.owner_id == current_user.id)

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
def read_by_id_task(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    task_id: int,
):
    task = service.get_task_by_id(db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMsg.TASK_NOT_FOUND
        )

    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMsg.TASK_FORBIDDEN,
        )

    return task


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        403: {"description": ErrorMsg.TASK_FORBIDDEN},
        404: {"description": ErrorMsg.TASK_NOT_FOUND},
        422: {"description": ErrorMsg.INVALID_CREDENTIALS},
    },
)
def update_task(
    db: Annotated[Session, Depends(get_db)],
    task_id: int,
    task_update: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
):
    task = service.get_task_by_id(db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMsg.TASK_NOT_FOUND
        )

    if task.owner_id != current_user.id:
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
    current_user: Annotated[User, Depends(get_current_user)],
):
    task = service.get_task_by_id(db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMsg.TASK_NOT_FOUND
        )

    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMsg.TASK_FORBIDDEN,
        )

    service.delete_task(db, task)

    return None
