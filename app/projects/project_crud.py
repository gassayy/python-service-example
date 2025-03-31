from datetime import datetime
from typing import Optional
from uuid import UUID
from psycopg import Connection, sql
from . import project_schemas


async def create_project(
    db: Connection,
    project: project_schemas.ProjectCreate
) -> project_schemas.Project:
    query = """
        INSERT INTO projects (name, description, status, owner_id, settings)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
    """
    async with db.cursor() as cur:
        await cur.execute(
            query,
            (
                project.name,
                project.description,
                project.status,
                project.owner_id,
                project.settings
            )
        )
        result = await cur.fetchone()
        return project_schemas.Project.model_validate(dict(zip([col.name for col in cur.description], result)))


async def get_project(db: Connection, project_id: UUID) -> Optional[project_schemas.Project]:
    query = "SELECT * FROM projects WHERE id = %s AND deleted_at IS NULL"
    async with db.cursor() as cur:
        await cur.execute(query, (project_id,))
        result = await cur.fetchone()
        if not result:
            return None
        return project_schemas.Project.model_validate(dict(zip([col.name for col in cur.description], result)))


async def get_paginated_projects(
    db: Connection,
    page: int = 1,
    results_per_page: int = 13,
    search: str = "",
) -> project_schemas.PaginatedProjects:
    offset = (page - 1) * results_per_page
    search_term = f"%{search}%"
    
    count_query = """
        SELECT COUNT(*) FROM projects 
        WHERE deleted_at IS NULL 
        AND (name ILIKE %s OR description ILIKE %s)
    """
    
    query = """
        SELECT * FROM projects 
        WHERE deleted_at IS NULL 
        AND (name ILIKE %s OR description ILIKE %s)
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    
    async with db.cursor() as cur:
        await cur.execute(count_query, (search_term, search_term))
        total = (await cur.fetchone())[0]
        
        await cur.execute(
            query,
            (search_term, search_term, results_per_page, offset)
        )
        results = await cur.fetchall()
        items = [
            project_schemas.Project.model_validate(dict(zip([col.name for col in cur.description], row)))
            for row in results
        ]
        
    return project_schemas.PaginatedProjects(total=total, items=items)


async def update_project(
    db: Connection,
    project_id: UUID,
    project: project_schemas.ProjectUpdate
) -> Optional[project_schemas.Project]:
    update_fields = {
        k: v for k, v in project.model_dump().items()
        if v is not None
    }
    if not update_fields:
        return await get_project(db, project_id)

    update_fields["updated_at"] = datetime.now()
    
    query = sql.SQL("""
        UPDATE projects
        SET {} 
        WHERE id = %s AND deleted_at IS NULL
        RETURNING *
    """).format(
        sql.SQL(", ").join(
            sql.SQL("{} = %s").format(sql.Identifier(k))
            for k in update_fields.keys()
        )
    )
    
    async with db.cursor() as cur:
        await cur.execute(
            query,
            (*update_fields.values(), project_id)
        )
        result = await cur.fetchone()
        if not result:
            return None
        return project_schemas.Project.model_validate(dict(zip([col.name for col in cur.description], result)))


async def delete_project(db: Connection, project_id: UUID) -> bool:
    query = """
        UPDATE projects
        SET deleted_at = CURRENT_TIMESTAMP, is_active = false
        WHERE id = %s AND deleted_at IS NULL
        RETURNING id
    """
    async with db.cursor() as cur:
        await cur.execute(query, (project_id,))
        return bool(await cur.fetchone()) 