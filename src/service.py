from typing import Optional
from sqlalchemy.orm import Session
from .database import Task
from fastapi import HTTPException, status
from .schemas.tasks import TaskStatus, TaskPriority, TaskUpdate
from .messages import ErrorMsg
from typing import Annotated
from fastapi import Depends
from .dependencies import get_db


def delete_task(db = Annotated[Session, Depends(get_db)], task: Task = Task) -> None:
    db.delete(task)
    db.commit()


def get_task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(db: Annotated[Session, Depends(get_db)], task: Task, task_update: TaskUpdate) -> Task:
    update_data = task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if key == "status" and value not in [s.value for s in TaskStatus]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ErrorMsg.INVALID_STATUS,
            )
        if key == "priority" and value not in [p.value for p in TaskPriority]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ErrorMsg.INVALID_PRIORITY,
            )
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task
