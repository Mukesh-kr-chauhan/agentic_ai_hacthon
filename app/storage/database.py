import json
import sqlite3
from typing import Any, Dict, List, Optional
from app.protocols.message_schema import AgentMessage

class Database:
    def __init__(self, db_path: str = "netcoop.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raw_input TEXT,
                report TEXT,
                status TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                incident_id TEXT,
                sender TEXT,
                receiver TEXT,
                message_type TEXT,
                timestamp TEXT,
                payload TEXT
            )
        """)
        conn.commit()
        conn.close()

    async def create_incident(self, incident_id: str, raw_input: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO incidents (incident_id, raw_input, status) VALUES (?, ?, ?)",
            (incident_id, json.dumps(raw_input), "running")
        )
        conn.commit()
        conn.close()

    async def update_incident_report(self, incident_id: str, report: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "UPDATE incidents SET report = ?, status = ? WHERE incident_id = ?",
            (json.dumps(report), report.get("status", "diagnosed"), incident_id)
        )
        conn.commit()
        conn.close()

    async def save_message(self, msg: AgentMessage):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?, ?, ?)",
            (msg.message_id, msg.incident_id, msg.sender.value, msg.receiver.value,
             msg.message_type.value, msg.timestamp, json.dumps(msg.payload))
        )
        conn.commit()
        conn.close()

    async def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT incident_id, created_at, raw_input, report, status FROM incidents WHERE incident_id = ?", (incident_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "incident_id": row[0],
            "created_at": row[1],
            "raw_input": json.loads(row[2]) if row[2] else {},
            "report": json.loads(row[3]) if row[3] else None,
            "status": row[4]
        }

    async def list_incidents(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT incident_id, created_at, status, report FROM incidents ORDER BY created_at DESC LIMIT 50")
        rows = cur.fetchall()
        conn.close()
        results = []
        for r in rows:
            rep = json.loads(r[3]) if r[3] else {}
            results.append({
                "incident_id": r[0],
                "created_at": r[1],
                "status": r[2],
                "suspected_root_cause": rep.get("suspected_root_cause", "In Progress"),
                "confidence": rep.get("confidence", 0.0),
                "severity": rep.get("severity", "medium")
            })
        return results

db = Database()