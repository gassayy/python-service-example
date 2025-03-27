CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);
"""

def init_db(conn):
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
        conn.commit() 