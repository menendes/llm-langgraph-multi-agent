from typing import Dict, List, Tuple, Callable
from state import Event

Rule = Tuple[Callable[[Event], bool], int, str]

SUSPICIOUS_UA = {"curl", "python", "nmap", "sqlmap"}

RULES: List[Rule] = [
    (lambda e: e["http_status"] in {401, 403, 500, 502, 503}, 25, "HTTP error status"),
    (lambda e: bool(e["threat_signature"]), 40, "IDS/IPS threat signature"),
    (lambda e: e["method"] not in {"GET", "HEAD", "OPTIONS"}, 10, "Non‑idempotent HTTP method"),
    (
        lambda e: e["bytes_received"] == 0 and e["bytes_sent"] > 1000,
        10,
        "Large upload with zero response – possible exfil",
    ),
    (
        lambda e: e["dst_port"] not in {80, 443, 22, 53},
        5,
        "Uncommon destination port",
    ),
    (
        lambda e: any(ua in e["user_agent"].lower() for ua in SUSPICIOUS_UA),
        10,
        "Suspicious user‑agent string",
    ),
    (
        lambda e: e["protocol"].upper() not in {"HTTP", "HTTPS", "SSH", "DNS"},
        5,
        "Unusual protocol",
    ),
]

MAX_SCORE = 100

def event_analysis(event: Event) -> Dict[str, object]:  # noqa: D401 – simple
    """Compute a heuristic **risk_score** plus rule breakdown."""
    score = 0
    hits: List[str] = []
    for cond, weight, desc in RULES:
        if cond(event):
            score += weight
            hits.append(desc)
    score = min(score, MAX_SCORE)
    return {"risk_score": score, "reasons": hits}