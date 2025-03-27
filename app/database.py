from psycopg import pool
from psycopg.rows import dict_rows

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fastapi_example"

# Create a connection pool
connection_pool = pool.ConnectionPool(
    DATABASE_URL,
    min_size=1,
    max_size=10,
    row_factory=dict_rows
)

def get_db():
    with connection_pool.connection() as conn:
        yield conn 