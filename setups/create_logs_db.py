import sqlite3
import os

# Path to database
db_path = os.path.join(os.path.dirname(__file__), "../data/logs.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS logins (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    ip TEXT,
    username TEXT,
    result TEXT,
    auth_method TEXT,
    device TEXT,
    country TEXT,
    mfa_required INTEGER
);
"""

_DUMMY = [
    ("2025-05-18T11:55:00Z", "203.0.113.45", "alice", "failure", "password", "chrome-win", "US", 1),
    ("2025-05-18T11:56:10Z", "203.0.113.45", "alice", "failure", "password", "chrome-win", "US", 1),
    ("2025-05-18T11:57:22Z", "203.0.113.45", "alice", "success", "password", "chrome-win", "US", 1),
    ("2025-05-18T12:03:41Z", "198.51.100.77", "bob",   "failure", "totp",     "ff-linux",  "GB", 1),
    ("2025-05-18T12:05:05Z", "198.51.100.77", "bob",   "failure", "totp",     "ff-linux",  "GB", 1),
    ("2025-05-18T12:07:30Z", "198.51.100.77", "bob",   "success", "oauth",    "edge-win",  "GB", 0),
]

def _init_db():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(_SCHEMA)
    cur.executemany(
        "INSERT OR IGNORE INTO logins(timestamp,ip,username,result,auth_method,device,country,mfa_required) VALUES (?,?,?,?,?,?,?,?)",
        _DUMMY,
    )
    conn.commit(); conn.close()

_init_db()

print("✅ logs.db created and populated!")
