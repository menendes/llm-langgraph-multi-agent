import sqlite3
import os

# Path to database
db_path = os.path.join(os.path.dirname(__file__), "../data/logs.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Connect to SQLite database (creates it if not exists)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop existing table (if re-running script)
cursor.execute("DROP TABLE IF EXISTS logs")

# Create table
cursor.execute("""
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    ip_address TEXT,
    event_type TEXT,
    success BOOLEAN
)
""")

# Insert sample log entries
sample_logs = [
    ("2025-04-01T10:12:00", "192.168.1.10", "login", 0),
    ("2025-04-01T10:15:00", "192.168.1.11", "login", 1),
    ("2025-04-01T10:20:00", "203.0.113.50", "login", 0),
    ("2025-04-02T09:00:00", "198.51.100.25", "password_reset", 1),
]

cursor.executemany("INSERT INTO logs (timestamp, ip_address, event_type, success) VALUES (?, ?, ?, ?)", sample_logs)

# Commit and close
conn.commit()
conn.close()

print("✅ logs.db created and populated!")