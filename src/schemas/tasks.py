from typing import Annotated, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    DOING = "doing"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class BaseTask(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title task")
    description: Annotated[str | None, Field(max_length=2000)] = None
    status: TaskStatus = Field(TaskStatus.PENDING)
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskCreate(BaseTask):
    pass


class TaskUpdate(BaseModel):
    # All optional fields to partial update
    title: Annotated[str | None, Field(min_length=1, max_length=200)] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseTask):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int  # user that created it
