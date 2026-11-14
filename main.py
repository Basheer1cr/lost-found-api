from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI(title="Lost & Found API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect("lostfound.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            place TEXT,
            date TEXT,
            contact TEXT,
            status TEXT DEFAULT 'open'
        )
    """)
    conn.commit()
    conn.close()

init_db()

class ItemCreate(BaseModel):
    type: str
    title: str
    description: Optional[str] = ""
    place: str
    date: str
    contact: str

@app.get("/")
def home():
    return {"message": "Lost & Found API is running"}

@app.post("/lost")
def report_lost(item: ItemCreate):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO items (type, title, description, place, date, contact, status) VALUES (?, ?, ?, ?, ?, ?, 'open')",
        ("lost", item.title, item.description, item.place, item.date, item.contact)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"message": "Lost item reported", "id": new_id}

@app.post("/found")
def report_found(item: ItemCreate):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO items (type, title, description, place, date, contact, status) VALUES (?, ?, ?, ?, ?, ?, 'open')",
        ("found", item.title, item.description, item.place, item.date, item.contact)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"message": "Found item reported", "id": new_id}

@app.get("/items")
def get_items(type: Optional[str] = None, search: Optional[str] = None):
    conn = get_db()
    query = "SELECT * FROM items WHERE 1=1"
    params = []
    if type:
        query += " AND type = ?"
        params.append(type)
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/items/{item_id}")
def get_one(item_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if not row:
        return {"error": "Item not found"}
    return dict(row)

@app.put("/items/{item_id}/returned")
def mark_returned(item_id: int):
    conn = get_db()
    conn.execute("UPDATE items SET status = 'returned' WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"message": f"Item {item_id} marked as returned"}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = get_db()
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"message": "Item deleted"}