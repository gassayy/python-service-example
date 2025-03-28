from fastapi import FastAPI, Depends, HTTPException
from typing import List
import uvicorn
from psycopg import Connection
import signal
import sys

from app.database import get_db, connection_pool
from app import models, schemas

app = FastAPI(title="FastAPI Example")

def signal_handler(sig, frame):
    print("\nClosing connection pool...")
    connection_pool.close()
    sys.exit(0)

@app.on_event("startup")
async def startup_event():
    with connection_pool.connection() as conn:
        models.init_db(conn)
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

@app.on_event("shutdown")
async def shutdown_event():
    connection_pool.close()

@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO items (title, description, is_active)
            VALUES (%s, %s, %s)
            RETURNING id, title, description, is_active
            """,
            (item.title, item.description, item.is_active)
        )
        result = cur.fetchone()
        conn.commit()
        return result

@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, description, is_active
            FROM items
            ORDER BY id
            LIMIT %s OFFSET %s
            """,
            (limit, skip)
        )
        return cur.fetchall()

@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, description, is_active
            FROM items
            WHERE id = %s
            """,
            (item_id,)
        )
        result = cur.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return result

if __name__ == "__main__":
    try:
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    finally:
        connection_pool.close()
