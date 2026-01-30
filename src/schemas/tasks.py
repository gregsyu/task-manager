from typing import Optional
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
    description: Optional[str] = Field(None, max_length=2000)
    status: TaskStatus = Field("pending")
    priority: Optional[TaskPriority] = Field("medium")
    due_date: Optional[datetime] = None


class TaskCreate(BaseTask):
    pass


class TaskUpdate(BaseTask):
    # All optional fields to partial update
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = Field(None)
    priority: Optional[TaskPriority] = Field(None)
    due_date: Optional[datetime] = None


class TaskResponse(BaseTask):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int  # user that created it
