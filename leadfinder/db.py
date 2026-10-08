import sqlite3
from datetime import date

SCHEMA = """
CREATE TABLE IF NOT EXISTS places (
    place_id     TEXT PRIMARY KEY,
    name         TEXT,
    address      TEXT,
    category     TEXT,
    status       TEXT,
    rating       REAL,
    review_count INTEGER,
    website      TEXT,
    maps_url     TEXT,
    first_seen   TEXT,
    last_seen    TEXT,
    contacted    INTEGER DEFAULT 0
);
"""


def connect(path="leads.db"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def upsert(conn, places):
    today = date.today().isoformat()
    new = 0
    for p in places:
        exists = conn.execute(
            "SELECT 1 FROM places WHERE place_id = ?", (p["place_id"],)
        ).fetchone()
        if exists:
            conn.execute(
                """UPDATE places SET name=?, address=?, category=?, status=?,
                   rating=?, review_count=?, website=?, maps_url=?, last_seen=?
                   WHERE place_id=?""",
                (p["name"], p["address"], p["category"], p["status"], p["rating"],
                 p["review_count"], p["website"], p["maps_url"], today, p["place_id"]),
            )
        else:
            conn.execute(
                """INSERT INTO places (place_id, name, address, category, status,
                   rating, review_count, website, maps_url, first_seen, last_seen)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (p["place_id"], p["name"], p["address"], p["category"], p["status"],
                 p["rating"], p["review_count"], p["website"], p["maps_url"], today, today),
            )
            new += 1
    conn.commit()
    return new


def all_places(conn):
    return [dict(row) for row in conn.execute("SELECT * FROM places")]
