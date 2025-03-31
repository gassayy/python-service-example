from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    settings: dict = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(ProjectBase):
    owner_id: UUID


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    settings: Optional[dict] = None
    is_active: Optional[bool] = None


class Project(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    is_active: bool
    owner_id: UUID


class PaginatedProjects(BaseModel):
    total: int
    items: List[Project] 