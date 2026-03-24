import sqlite3
import json
import os
from typing import List, Optional

from models import Activity, Reflection

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timelog.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            name TEXT NOT NULL,
            tags TEXT NOT NULL DEFAULT '[]',
            color TEXT NOT NULL DEFAULT '#4A90D9'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            activity_id TEXT PRIMARY KEY,
            good TEXT NOT NULL DEFAULT '["","",""]',
            bad TEXT NOT NULL DEFAULT '["","",""]',
            next_steps TEXT NOT NULL DEFAULT '["","",""]',
            FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


def _row_to_activity(row) -> Activity:
    return Activity(
        id=row[0],
        date=row[1],
        start_time=row[2],
        end_time=row[3],
        name=row[4],
        tags=json.loads(row[5]),
        color=row[6],
    )


def save_activity(activity: Activity):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO activities VALUES (?,?,?,?,?,?,?)",
        (activity.id, activity.date, activity.start_time, activity.end_time,
         activity.name, json.dumps(activity.tags, ensure_ascii=False), activity.color),
    )
    conn.commit()
    conn.close()


def get_activities_by_date(date: str) -> List[Activity]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT * FROM activities WHERE date=? ORDER BY start_time", (date,)
    ).fetchall()
    conn.close()
    return [_row_to_activity(r) for r in rows]


def delete_activity(activity_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM activities WHERE id=?", (activity_id,))
    conn.execute("DELETE FROM reflections WHERE activity_id=?", (activity_id,))
    conn.commit()
    conn.close()


def save_reflection(reflection: Reflection):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO reflections VALUES (?,?,?,?)",
        (
            reflection.activity_id,
            json.dumps(reflection.good, ensure_ascii=False),
            json.dumps(reflection.bad, ensure_ascii=False),
            json.dumps(reflection.next_steps, ensure_ascii=False),
        ),
    )
    conn.commit()
    conn.close()


def get_reflection(activity_id: str) -> Optional[Reflection]:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT * FROM reflections WHERE activity_id=?", (activity_id,)
    ).fetchone()
    conn.close()
    if row:
        return Reflection(
            activity_id=row[0],
            good=json.loads(row[1]),
            bad=json.loads(row[2]),
            next_steps=json.loads(row[3]),
        )
    return None


def search_by_tag(tag: str) -> List[dict]:
    """Return list of {activity, reflection} dicts matching the tag."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT * FROM activities WHERE tags LIKE ? ORDER BY date DESC, start_time",
        (f'%"{tag}"%',),
    ).fetchall()
    results = []
    for row in rows:
        activity = _row_to_activity(row)
        ref_row = conn.execute(
            "SELECT * FROM reflections WHERE activity_id=?", (activity.id,)
        ).fetchone()
        reflection = None
        if ref_row:
            reflection = Reflection(
                activity_id=ref_row[0],
                good=json.loads(ref_row[1]),
                bad=json.loads(ref_row[2]),
                next_steps=json.loads(ref_row[3]),
            )
        results.append({"activity": activity, "reflection": reflection})
    conn.close()
    return results
