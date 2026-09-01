"""
Database module — SQLite via aiosqlite for verification history.
"""
import aiosqlite
from pathlib import Path
from datetime import datetime
from typing import List, Dict

DB_PATH = Path(__file__).parent / "bharatshield.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verification_id TEXT NOT NULL,
                document_type TEXT,
                trust_score INTEGER,
                risk_level TEXT,
                filename TEXT,
                created_at TEXT
            )
        """)
        await db.commit()


async def save_verification(
    verification_id: str,
    document_type: str,
    trust_score: int,
    risk_level: str,
    filename: str,
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO verifications
                (verification_id, document_type, trust_score, risk_level, filename, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                verification_id,
                document_type,
                trust_score,
                risk_level,
                filename,
                datetime.utcnow().isoformat(),
            ),
        )
        await db.commit()


async def get_all_verifications() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM verifications ORDER BY created_at DESC LIMIT 100"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
