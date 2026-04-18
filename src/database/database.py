import sqlite3
import pandas as pd
import os
from datetime import datetime

class DetectionDatabase:
    def __init__(self, db_path="logs/detections.db"):
        """Initialize database — creates file if it doesn't exist"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
        print("✅ Database initialized!")

    def init_db(self):
        """Create the events table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT NOT NULL,
                confidence  REAL,
                zone        TEXT,
                snapshot    TEXT,
                alert_type  TEXT DEFAULT 'intrusion'
            )
        """)
        conn.commit()
        conn.close()

    def log_event(self, timestamp, confidence, zone, snapshot):
        """Insert a new detection event into the database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO events(timestamp, confidence, zone, snapshot) VALUES(?,?,?,?)",
            (timestamp, confidence, zone, snapshot)
        )
        conn.commit()
        conn.close()

    def get_all_events(self):
        """Return all events as a Pandas DataFrame"""
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(
                "SELECT * FROM events ORDER BY id DESC", conn
            )
        except Exception:
            df = pd.DataFrame()
        conn.close()
        return df

    def get_event_count(self):
        """Return total number of logged events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def export_csv(self, path="logs/export.csv"):
        """Export all events to a CSV file"""
        df = self.get_all_events()
        df.to_csv(path, index=False)
        print(f"📊 Exported {len(df)} events to {path}")
        return path