from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

DATABASE_URL = "postgresql://postgres:131425@localhost:5432/fastapi_example"

# Create a connection pool
connection_pool = ConnectionPool(
    DATABASE_URL,
    min_size=1,
    max_size=10
)

def get_db():
    with connection_pool.connection() as conn:
        # Set the row factory on the connection
        conn.row_factory = dict_row
        yield conn 