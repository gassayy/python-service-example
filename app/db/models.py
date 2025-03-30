import json
from datetime import timedelta, datetime, timezone
from io import BytesIO
from re import sub
from typing import TYPE_CHECKING, Annotated, Optional, Self
from uuid import UUID

from fastapi import HTTPException
from loguru import logger as log
from psycopg import Connection
from psycopg.rows import class_row
from pydantic import BaseModel, AwareDatetime

from app.db.enums import (
    HTTPStatus,
    UserRole,
    ProjectRole,
)
if TYPE_CHECKING:
    from app.users.user_schemas import UserIn, UserUpdate
    from app.tasks.task_schemas import TaskCreate, TaskUpdate

def dump_and_check_model(db_model: BaseModel):
    """Dump the Pydantic model, removing None and default values.

    Also validates to check the model is not empty for insert / update.
    """
    model_dump = db_model.model_dump(exclude_none=True, exclude_unset=True)

    if not model_dump:
        log.error("Attempted create or update with no data.")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="No data provided."
        )

    return model_dump


class DbUserRole(BaseModel):
    """Table user_roles."""

    user_id: int
    project_id: int
    role: ProjectRole

    @classmethod
    async def create(
        cls,
        db: Connection,
        project_id: int,
        user_id: int,
        role: ProjectRole,
    ) -> Self:
        """Create a new user role."""
        async with db.cursor(row_factory=class_row(cls)) as cur:
            params = {
                "project_id": project_id,
                "user_id": user_id,
                "role": role.name,
            }
            await cur.execute(
                """
                INSERT INTO user_roles
                    (user_id, project_id, role)
                VALUES
                    (%(user_id)s, %(project_id)s, %(role)s)
                    ON CONFLICT (user_id, project_id) DO UPDATE
                    SET role = EXCLUDED.role
                    WHERE user_roles.role < EXCLUDED.role;
            """,
                params,
            )

            # NOTE this will return the latest role, even if it's not updated
            # to make sure something is always returned
            await cur.execute(
                """
                SELECT * FROM user_roles
                WHERE user_id = %(user_id)s AND project_id = %(project_id)s;
            """,
                params,
            )
            latest_role = await cur.fetchone()

        if latest_role is None:
            msg = f"Failed to create user role: {params}"
            log.error(msg)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=msg
            )

        return latest_role

    @classmethod
    async def all(
        cls,
        db: Connection,
        project_id: Optional[int] = None,
    ) -> Optional[list[Self]]:
        """Fetch all project user roles."""
        filters = []
        params = {}
        if project_id:
            filters.append(f"project_id = {project_id}")
            params["project_id"] = project_id

        sql = f"""
            SELECT * FROM user_roles
            {"WHERE " + " AND ".join(filters) if filters else ""}
        """
        async with db.cursor(row_factory=class_row(cls)) as cur:
            await cur.execute(
                sql,
            )
            return await cur.fetchall()
        
class DbUser(BaseModel):
    """Table users."""

    id: int  # NOTE normally the OSM ID
    username: str
    role: Optional[UserRole] = None
    profile_img: Optional[str] = None
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    email_address: Optional[str] = None
    is_email_verified: Optional[bool] = False
    is_expert: Optional[bool] = False
    api_key: Optional[str] = None
    registered_at: Optional[AwareDatetime] = None
    last_login_at: Optional[AwareDatetime] = None

    # Relationships
    project_roles: Optional[dict[int, ProjectRole]] = None  # project:role pairs
    orgs_managed: Optional[list[int]] = None

    @classmethod
    async def one(cls, db: Connection, user_identifier: int | str) -> Self:
        """Get a user either by ID or username, including roles and orgs managed."""
        async with db.cursor(row_factory=class_row(cls)) as cur:
            sql = """
                SELECT
                    u.*,

                -- Aggregate project roles for the user, as project:role pairs
                jsonb_object_agg(
                COALESCE(ur.project_id),
                    COALESCE(ur.role, 'MAPPER')
                ) FILTER (WHERE ur.project_id IS NOT NULL) AS roles

                FROM users u
                LEFT JOIN user_roles ur ON u.id = ur.user_id
            """

            if isinstance(user_identifier, int):
                # Is ID
                sql += """
                    WHERE u.id = %(user_identifier)s
                    GROUP BY u.id;
                """
            else:
                # Is username (basic flexible matching)
                sql += """
                    WHERE u.username ILIKE %(user_identifier)s
                    GROUP BY u.id;
                """
                user_identifier = f"{user_identifier}%"
            await cur.execute(
                sql,
                {"user_identifier": user_identifier},
            )
            db_user = await cur.fetchone()

        if db_user is None:
            raise KeyError(f"User ({user_identifier}) not found.")

        return db_user

    @classmethod
    async def all(
        cls,
        db: Connection,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Optional[list[Self]]:
        """Fetch all users."""
        filters = []
        params = {"offset": skip, "limit": limit} if skip and limit else {}

        if search:
            filters.append("username ILIKE %(search)s")
            params["search"] = f"%{search}%"

        sql = f"""
            SELECT * FROM users
            {"WHERE " + " AND ".join(filters) if filters else ""}
            ORDER BY registered_at DESC
        """
        sql += (
            """
            OFFSET %(offset)s
            LIMIT %(limit)s;
        """
            if skip and limit
            else ";"
        )
        async with db.cursor(row_factory=class_row(cls)) as cur:
            log.info(f"Executing query: {sql!r} with params: {params!r}")
            await cur.execute(
                sql,
                params,
            )
            return await cur.fetchall()

    @classmethod
    async def delete(cls, db: Connection, user_id: int) -> bool:
        """Delete a user and their related data."""
        async with db.cursor() as cur:
            await cur.execute(
                """
                DELETE FROM user_roles WHERE user_id = %(user_id)s;
            """,
                {"user_id": user_id},
            )
            await cur.execute(
                """
                DELETE FROM users WHERE id = %(user_id)s;
            """,
                {"user_id": user_id},
            )

    @classmethod
    async def create(
        cls,
        db: Connection,
        user_in: "UserIn",
        ignore_conflict: bool = False,
    ) -> Self:
        """Create a new user."""
        if not ignore_conflict and cls.one(db, user_in.username):
            msg = f"Username ({user_in.username}) already exists!"
            log.warning(f"Failed to create new user: {msg}")
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=msg)

        model_dump = dump_and_check_model(user_in)
        columns = ", ".join(model_dump.keys())
        value_placeholders = ", ".join(f"%({key})s" for key in model_dump.keys())
        conflict_statement = """
            ON CONFLICT ("username") DO UPDATE
            SET
                role = EXCLUDED.role,
                mapping_level = EXCLUDED.mapping_level,
                name = EXCLUDED.name,
                api_key = EXCLUDED.api_key
        """

        sql = f"""
            INSERT INTO users
                ({columns})
            VALUES
                ({value_placeholders})
            {conflict_statement if ignore_conflict else ""}
            RETURNING *;
        """

        async with db.cursor(row_factory=class_row(cls)) as cur:
            await cur.execute(sql, model_dump)
            new_user = await cur.fetchone()

        if new_user is None:
            msg = f"Unknown SQL error for data: {model_dump}"
            log.error(f"Failed user creation: {model_dump}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=msg
            )

        return new_user

    @classmethod
    async def update(
        cls, db: Connection, user_id: int, user_update: "UserUpdate"
    ) -> Self:
        """Update the role of a specific user."""
        model_dump = dump_and_check_model(user_update)
        placeholders = [f"{key} = %({key})s" for key in model_dump.keys()]
        sql = f"""
            UPDATE users
            SET {", ".join(placeholders)}
            WHERE id = %(user_id)s
            RETURNING *;
        """

        async with db.cursor(row_factory=class_row(cls)) as cur:
            await cur.execute(
                sql,
                {"user_id": user_id, **model_dump},
            )
            updated_user = await cur.fetchone()

        if updated_user is None:
            msg = f"Failed to update user with ID: {user_id}"
            log.error(msg)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=msg
            )

        return updated_user

class DbTask(BaseModel):
    """Table tasks."""

    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[AwareDatetime] = None
    is_completed: bool = False
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @classmethod
    async def one(cls, db: Connection, task_id: int) -> Self:
        """Get a single task by ID.

        Args:
            db: Database connection
            task_id: ID of the task to retrieve

        Raises:
            KeyError: If task not found

        Returns:
            Self: Task object
        """
        async with db.cursor(row_factory=class_row(cls)) as cur:
            await cur.execute(
                """
                SELECT * FROM tasks
                WHERE id = %(task_id)s;
                """,
                {"task_id": task_id},
            )
            db_task = await cur.fetchone()

        if db_task is None:
            raise KeyError(f"Task ({task_id}) not found.")

        return db_task

    @classmethod
    async def all(
        cls,
        db: Connection,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
    ) -> list[Self]:
        """Fetch all tasks with optional filtering.

        Args:
            db: Database connection
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search term for filtering tasks

        Returns:
            list[Self]: List of task objects
        """
        filters = []
        params = {"offset": skip, "limit": limit} if skip and limit else {}

        if search:
            filters.append(
                "(title ILIKE %(search)s OR description ILIKE %(search)s)"
            )
            params["search"] = f"%{search}%"

        sql = f"""
            SELECT * FROM tasks
            {"WHERE " + " AND ".join(filters) if filters else ""}
            ORDER BY created_at DESC
        """
        sql += (
            """
            OFFSET %(offset)s
            LIMIT %(limit)s;
        """
            if skip and limit
            else ";"
        )

        async with db.cursor(row_factory=class_row(cls)) as cur:
            log.info(f"Executing query: {sql!r} with params: {params!r}")
            await cur.execute(sql, params)
            return await cur.fetchall()

    @classmethod
    async def create(
        cls,
        db: Connection,
        task_in: "TaskCreate",
    ) -> Self:
        """Create a new task.

        Args:
            db: Database connection
            task_in: Task creation data

        Raises:
            HTTPException: If creation fails

        Returns:
            Self: Created task object
        """
        model_dump = dump_and_check_model(task_in)
        now = datetime.now(timezone.utc)
        
        # Add timestamps
        model_dump.update({
            "created_at": now,
            "updated_at": now,
        })
        
        columns = ", ".join(model_dump.keys())
        value_placeholders = ", ".join(f"%({key})s" for key in model_dump.keys())

        sql = f"""
            INSERT INTO tasks
                ({columns})
            VALUES
                ({value_placeholders})
            RETURNING *;
        """

        async with db.cursor(row_factory=class_row(cls)) as cur:
            await cur.execute(sql, model_dump)
            new_task = await cur.fetchone()

        if new_task is None:
            msg = f"Failed to create task: {model_dump}"
            log.error(msg)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=msg
            )

        return new_task

    @classmethod
    async def update(
        cls, db: Connection, task_id: int, task_update: "TaskUpdate"
    ) -> Self:
        """Update an existing task.

        Args:
            db: Database connection
            task_id: ID of the task to update
            task_update: Task update data

        Raises:
            HTTPException: If update fails

        Returns:
            Self: Updated task object
        """
        model_dump = dump_and_check_model(task_update)
        model_dump["updated_at"] = datetime.now(timezone.utc)
        
        placeholders = [f"{key} = %({key})s" for key in model_dump.keys()]
        sql = f"""
            UPDATE tasks
            SET {", ".join(placeholders)}
            WHERE id = %(task_id)s
            RETURNING *;
        """

        async with db.cursor(row_factory=class_row(cls)) as cur:
            await cur.execute(
                sql,
                {"task_id": task_id, **model_dump},
            )
            updated_task = await cur.fetchone()

        if updated_task is None:
            msg = f"Failed to update task with ID: {task_id}"
            log.error(msg)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=msg
            )

        return updated_task

    @classmethod
    async def delete(cls, db: Connection, task_id: int) -> bool:
        """Delete a task.

        Args:
            db: Database connection
            task_id: ID of the task to delete

        Returns:
            bool: True if task was deleted, False otherwise
        """
        async with db.cursor() as cur:
            await cur.execute(
                """
                DELETE FROM tasks WHERE id = %(task_id)s;
                """,
                {"task_id": task_id},
            )
            return cur.rowcount > 0