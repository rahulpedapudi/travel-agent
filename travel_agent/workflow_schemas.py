"""
WORKFLOW SCHEMAS
================
Schemas for tracking agent workflow transparency.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    """Status of a task in the workflow."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class WorkflowTask(BaseModel):
    """Single task in the agent's plan."""
    id: str = Field(..., description="Unique ID for the task")
    label: str = Field(..., description="User-facing description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status")
    agent: Optional[str] = Field(None, description="Name of the agent handling this task")

class WorkflowPlan(BaseModel):
    """Overall plan of tasks."""
    tasks: List[WorkflowTask] = Field(default_factory=list, description="List of tasks")
    current_task_id: Optional[str] = Field(None, description="ID of the currently active task")
