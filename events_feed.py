from __future__ import annotations
import random, datetime as dt, itertools

from state import Event

_USER_BY_IP = {
    "203.0.113.45": "alice",
    "198.51.100.77": "bob",
    "192.0.2.13":   "carol",
}
_SIGS = ["Brute_force_login", "SQL_injection", "", "", "", "XSS_attempt"]
_METHODS = ["GET","POST","PUT"]

BASE_EVENT: Event = {
    "timestamp": "",
    "src_ip": "",
    "dst_ip": "10.20.30.40",
    "src_port": 443,
    "dst_port": 80,
    "protocol": "HTTP",
    "http_status": 200,
    "url": "/index.html",
    "method": "GET",
    "user_agent": "Mozilla/5.0",
    "threat_signature": "",
    "bytes_sent": 300,
    "bytes_received": 500,
}

def random_event() -> Event:
    e = BASE_EVENT.copy()
    e["timestamp"] = dt.datetime.utcnow().isoformat() + "Z"

    ip = random.choice(list(_USER_BY_IP))
    e["src_ip"] = ip
    e["username"] = _USER_BY_IP[ip]

    e["http_status"] = random.choice([200, 200, 401, 403, 500])
    e["method"]        = m = random.choice(["GET", "POST"])
    if m != "GET":
        e["bytes_sent"], e["bytes_received"] = random.randint(500, 5000), 0

    e["threat_signature"] = random.choice(["Brute_force_login", "", "", "XSS_attempt"])
    return e


def event_stream(limit: int | None = None):
    """Yield *limit* events (or infinite if None)."""
    for _ in itertools.count() if limit is None else range(limit):
        yield random_event()