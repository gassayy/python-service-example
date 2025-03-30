from typing import Annotated, List, Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from psycopg import Connection

from app.db.database import db_conn
from app.tasks.task_schemas import TaskCreate, TaskUpdate, TaskResponse
from app.tasks.task_crud import (
    create_task,
    get_task,
    get_paginated_tasks,
    update_task,
    delete_task,
)

# Create a type alias for the DB dependency
DbConn = Annotated[Connection, Depends(db_conn)]

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task: TaskCreate,
    db: DbConn,
):
    return await create_task(db, task)

@router.get("/{task_id}", response_model=TaskResponse)
async def read_task(
    task_id: int,
    db: DbConn,
):
    return await get_task(db, task_id)

@router.get("/", response_model=dict)
async def read_tasks(
    db: DbConn,
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
):
    return await get_paginated_tasks(db, page, limit, search)

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_existing_task(
    task_id: int,
    task: TaskUpdate,
    db: DbConn,
):
    return await update_task(db, task_id, task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_task(
    task_id: int,
    db: DbConn,
):
    await delete_task(db, task_id) 