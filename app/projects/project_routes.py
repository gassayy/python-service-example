from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg import Connection
from app.db.database import db_conn
from . import project_schemas, project_crud

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=project_schemas.Project)
async def create_project(
    project: project_schemas.ProjectCreate,
    db: Annotated[Connection, Depends(db_conn)]
):
    """Create a new project."""
    return await project_crud.create_project(db, project)


@router.get("", response_model=project_schemas.PaginatedProjects)
async def get_projects(
    db: Annotated[Connection, Depends(db_conn)],
    page: int = Query(1, ge=1),
    results_per_page: int = Query(13, le=100),
    search: str = "",
):
    """Get all projects with pagination."""
    return await project_crud.get_paginated_projects(db, page, results_per_page, search)


@router.get("/{project_id}", response_model=project_schemas.Project)
async def get_project(
    project_id: UUID,
    db: Annotated[Connection, Depends(db_conn)]
):
    """Get a specific project by ID."""
    project = await project_crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=project_schemas.Project)
async def update_project(
    project_id: UUID,
    project: project_schemas.ProjectUpdate,
    db: Annotated[Connection, Depends(db_conn)]
):
    """Update a project."""
    updated_project = await project_crud.update_project(db, project_id, project)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@router.delete("/{project_id}", response_model=bool)
async def delete_project(
    project_id: UUID,
    db: Annotated[Connection, Depends(db_conn)]
):
    """Soft delete a project."""
    if not await project_crud.delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return True 