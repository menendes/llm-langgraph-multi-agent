from typing import Annotated
from langgraph.prebuilt import InjectedState
from langchain.agents import Tool
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
ABUSE_IP_DB_KEY = os.getenv("ABUSE_IP_DB")

# ThreatIntel Tool
# Purpose: Query threat reputation for an IP address using AbuseIPDB API
# Input: JSON string with at least "ip_address"
# Output: JSON with abuse_score, country, usage_type, and domain

def threat_intel_agent(state: Annotated[dict, InjectedState]) -> str:
    try:
        if isinstance(state, str):
            event = json.loads(state)
        else:
            return json.dumps({"error": "Invalid input format"})

        ip = event.get("ip_address")
        if not ip:
            return json.dumps({"error": "Missing IP address"})

        response = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip, "maxAgeInDays": 90},
            headers={
                "Key": ABUSE_IP_DB_KEY,
                "Accept": "application/json"
            },
            timeout=5
        )

        data = response.json().get("data", {})
        return json.dumps({
            "abuse_score": data.get("abuseConfidenceScore", 0),
            "abuse_country": data.get("countryCode"),
            "abuse_usage_type": data.get("usageType"),
            "abuse_domain": data.get("domain")
        })

    except Exception as e:
        return json.dumps({"error": f"ThreatIntel error: {e}"})

threat_tool = Tool(
    name="ThreatIntel",
    func=threat_intel_agent,
    description="Look up IP address reputation using AbuseIPDB. Input must be a JSON object with 'ip_address'."
)