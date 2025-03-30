"""Logic for user routes."""

import os
from datetime import datetime, timedelta, timezone
from textwrap import dedent
from typing import Optional

from loguru import logger as log
from psycopg import Connection
from psycopg.rows import class_row

from app.db.models import DbUser
from app.db.utils import get_pagination

SVC_OSM_TOKEN = os.getenv("SVC_OSM_TOKEN", None)
WARNING_INTERVALS = [21, 14, 7]  # Days before deletion
INACTIVITY_THRESHOLD = 2 * 365  # 2 years approx


async def process_inactive_users(
    db: Connection,
):
    """Identify inactive users and delete accounts."""
    now = datetime.now(timezone.utc)
    warning_thresholds = [
        (now - timedelta(days=INACTIVITY_THRESHOLD - days))
        for days in WARNING_INTERVALS
    ]
    deletion_threshold = now - timedelta(days=INACTIVITY_THRESHOLD)

    async with db.cursor() as cur:
        # Users eligible for deletion
        async with db.cursor(row_factory=class_row(DbUser)) as cur:
            await cur.execute(
                """
                SELECT id, username
                FROM users
                WHERE last_login_at < %(deletion_threshold)s;
                """,
                {"deletion_threshold": deletion_threshold},
            )
            users_to_delete = await cur.fetchall()

        for user in users_to_delete:
            log.info(f"Deleting user {user.username} due to inactivity.")
            await DbUser.delete(db, user.id)


async def get_paginated_users(
    db: Connection,
    page: int,
    results_per_page: int,
    search: Optional[str] = None,
) -> dict:
    """Helper function to fetch paginated users with optional filters."""
    # Get subset of users
    users = await DbUser.all(db, search=search)
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page
    paginated_users = users[start_index:end_index]

    pagination = await get_pagination(
        page, len(paginated_users), results_per_page, len(users)
    )

    return {"results": paginated_users, "pagination": pagination}