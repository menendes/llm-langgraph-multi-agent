from typing import Annotated
from langgraph.prebuilt import InjectedState
from langchain.agents import Tool
import json

# LogMonitor Tool
# Purpose: Detect basic indicators of suspicious activity in a log event.
# Input: JSON string with log event fields (timestamp, ip_address, username, event_type, success, source)
# Output: JSON string containing "suspicious": true/false, and a short "reason"
def log_monitor_agent(state: Annotated[dict, InjectedState]) -> str:
    try:
        if isinstance(state, str):
            event = json.loads(state)
        else:
            return json.dumps({"error": "Invalid event input"})

        ip = event.get("ip_address", "unknown")
        username = event.get("username", "unknown")
        success = event.get("success", True)
        event_type = event.get("event_type", "unknown")
        source = event.get("source", "unknown")
        timestamp = event.get("timestamp", "unknown")

        if not success and event_type == "login":
            return json.dumps({
                "suspicious": True,
                "reason": f"Failed login attempt by user '{username}' from IP {ip} at {timestamp} via {source}."
            })

        return json.dumps({
            "suspicious": False,
            "reason": f"Normal event: {event_type} by {username} from IP {ip}."
        })

    except Exception as e:
        return json.dumps({"error": f"LogMonitor error: {e}"})

log_tool = Tool(
    name="LogMonitor",
    func=log_monitor_agent,
    description="Analyze a JSON log event to determine if it shows signs of suspicious behavior (e.g., failed login). Returns a JSON object with a suspicion flag and explanation."
)