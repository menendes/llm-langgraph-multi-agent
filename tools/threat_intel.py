import os
from typing import Dict, Optional

import requests

API_KEY = os.getenv("ABUSE_IP_DB", "")
API_URL = "https://api.abuseipdb.com/api/v2/check"
HEADERS = {"Key": API_KEY, "Accept": "application/json"}

# Fields we commonly care about (the API returns many more)
KEEP = {
    "abuseConfidenceScore": "abuse_score",
    "isWhitelisted": "is_whitelisted",
    "totalReports": "total_reports",
    "lastReportedAt": "last_reported_at",
    "countryCode": "country_code",
    "usageType": "usage_type",
    "isp": "isp",
    "domain": "domain",
}


def _call_api(ip: str, max_age: int) -> Optional[dict]:
    try:
        resp = requests.get(
            API_URL,
            params={"ipAddress": ip, "maxAgeInDays": max_age},
            headers=HEADERS,
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json().get("data")
    except Exception:
        return None


def threat_intel(ip: str, max_age: int = 90) -> Dict[str, object]:
    """Query AbuseIPDB; return selected fields or an error structure."""
    if not API_KEY:
        return {"abuse_score": None, "error": "ABUSE_IP_DB_KEY not set"}

    data = _call_api(ip, max_age)
    if not data:
        return {"abuse_score": None, "error": "AbuseIPDB request failed"}

    out: Dict[str, object] = {}
    for api_field, our_key in KEEP.items():
        out[our_key] = data.get(api_field)

    return out