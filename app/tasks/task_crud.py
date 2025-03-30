"""Logic for task routes."""

from datetime import datetime, timezone
from typing import List, Optional
from http import HTTPStatus

from loguru import logger as log
from psycopg import Connection
from psycopg.rows import class_row
from fastapi import HTTPException

from app.db.models import DbTask
from app.db.utils import get_pagination
from app.tasks.task_schemas import TaskCreate, TaskUpdate


async def get_paginated_tasks(
    db: Connection,
    page: int,
    results_per_page: int,
    search: Optional[str] = None,
) -> dict:
    """Helper function to fetch paginated tasks with optional filters."""
    try:
        tasks = await DbTask.all(
            db, 
            skip=(page - 1) * results_per_page,
            limit=results_per_page,
            search=search
        )
        
        total_tasks = len(await DbTask.all(db, search=search))
        
        pagination = await get_pagination(
            page, len(tasks), results_per_page, total_tasks
        )

        return {"results": tasks or [], "pagination": pagination}
    except Exception as e:
        log.error(f"Error fetching paginated tasks: {e}")
        return {"results": [], "pagination": None}


async def create_task(db: Connection, task: TaskCreate) -> DbTask:
    """Create a new task in the database."""
    try:
        new_task = await DbTask.create(db, task)
        if not new_task:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )
        return new_task
    except Exception as e:
        log.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def get_task(db: Connection, task_id: int) -> DbTask:
    """Retrieve a single task by ID."""
    try:
        task = await DbTask.one(db, task_id)
        if not task:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
        return task
    except KeyError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    except Exception as e:
        log.error(f"Error fetching task {task_id}: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def update_task(
    db: Connection, task_id: int, task: TaskUpdate
) -> DbTask:
    """Update an existing task."""
    try:
        updated_task = await DbTask.update(db, task_id, task)
        if not updated_task:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
        return updated_task
    except Exception as e:
        log.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def delete_task(db: Connection, task_id: int) -> None:
    """Delete a task from the database."""
    try:
        deleted = await DbTask.delete(db, task_id)
        if not deleted:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
    except Exception as e:
        log.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 