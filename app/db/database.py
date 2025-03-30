from typing import cast
from typing import AsyncGenerator

from fastapi import Request
from psycopg import Connection
from psycopg_pool import AsyncConnectionPool
from loguru import logger as log

from app.config import settings

def get_db_connection_pool() -> AsyncConnectionPool:
    """Get the connection pool for psycopg.

    NOTE the pool connection is opened in the FastAPI server startup (lifespan).
    """
    log.info(f"DB_CONN_URL: {settings.DB_CONN_URL}")
    return AsyncConnectionPool(
        conninfo=settings.DB_CONN_URL, open=False
    )

async def db_conn(request: Request) -> AsyncGenerator[Connection, None]:
    """Get a connection from the psycopg pool.

    Info on connections vs cursors:
    https://www.psycopg.org/psycopg3/docs/advanced/async.html

    Here we are getting a connection from the pool, which will be returned
    after the session ends / endpoint finishes processing.

    In summary:
    - Connection is created on endpoint call.
    - Cursors are used to execute commands throughout endpoint.
      Note it is possible to create multiple cursors from the connection,
      but all will be executed in the same db 'transaction'.
    - Connection is closed on endpoint finish.

    -----------------------------------
    To use the connection in endpoints:
    -----------------------------------

    @app.get("/something")
    async def do_stuff(db = Depends(db_conn)):
        async with db.cursor() as cursor:
            await cursor.execute("SELECT * FROM items")
            result = await cursor.fetchall()
            return result

    -----------------------------------
    Additionally, the connection could be passed through to a function to
    utilise the Pydantic model serialisation on the cursor:
    -----------------------------------

    from psycopg.rows import class_row
    async def get_user_by_id(db: Connection, id: int):
        async with db.cursor(row_factory=class_row(User)) as cur:
            await cur.execute(
                '''
                SELECT id, first_name, last_name, dob
                FROM (VALUES
                    (1, 'John', 'Doe', '2000-01-01'::date),
                    (2, 'Jane', 'White', NULL)
                ) AS data (id, first_name, last_name, dob)
                WHERE id = %(id)s;
                ''',
                {"id": id},
            )
            obj = await cur.fetchone()

            # reveal_type(obj) would return 'Optional[User]' here

            if not obj:
                raise KeyError(f"user {id} not found")

            # reveal_type(obj) would return 'User' here

            return obj
    """
    db_pool = cast(AsyncConnectionPool, request.state.db_pool)
    async with db_pool.connection() as conn:
        yield conn