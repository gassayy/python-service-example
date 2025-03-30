"""User dependencies for use in Depends."""

from typing import Annotated

from fastapi import Depends
from fastapi.exceptions import HTTPException
from psycopg import Connection

from app.db.database import db_conn
from app.db.enums import HTTPStatus
from app.db.models import DbUser


async def get_user(
    id: str | int, db: Annotated[Connection, Depends(db_conn)]
) -> DbUser:
    """Return a user from the DB, else exception.

    Args:
        id (str | int): The user ID (integer) or username (string) to check.
        db (Connection): The database connection.

    Returns:
        DbUser: The user if found.

    Raises:
        HTTPException: Raised with a 404 status code if the user is not found.
    """
    try:
        try:
            # Is ID (int)
            id = int(id)
        except ValueError:
            # Is username (str)
            pass
        return await DbUser.one(db, id)
    except KeyError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e