from typing import Annotated
from langgraph.prebuilt import InjectedState
from langchain.agents import Tool
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Notifier Tool
# Purpose: Send security alerts to Slack when LLM determines an event is threatening
# Input: JSON string enriched with relevant fields (e.g. username, ip_address, abuse_score, fail counts, etc.)
# Output: Text result indicating success/failure of notification

def notifier_agent(state: Annotated[dict, InjectedState]) -> str:
    try:
        if isinstance(state, str):
            event = json.loads(state)
        else:
            return json.dumps({"error": "Invalid input format"})

        ip = event.get("ip_address", "unknown")
        username = event.get("username", "unknown")
        abuse_score = event.get("abuse_score", "unknown")
        ip_fails = event.get("ip_fail_count", 0)
        user_fails = event.get("user_fail_count", 0)
        timestamp = event.get("timestamp", "unknown")

        alert_msg = (
            f"*Security Alert!*"
            f"- Timestamp: {timestamp}\n"
            f"- User: {username}\n"
            f"- IP: {ip}\n"
            f"- Abuse Score: {abuse_score}/100\n"
            f"- IP Failures: {ip_fails}\n"
            f"- Username Failures: {user_fails}\n"
            f"Recommendation: Investigate this login event and apply mitigation if needed."
        )

        if SLACK_WEBHOOK_URL:
            res = requests.post(SLACK_WEBHOOK_URL, json={"text": alert_msg})
            if res.status_code == 200:
                return "✅ Alert sent to Slack."
            else:
                return f"❌ Slack error: {res.text}"
        else:
            return "⚠️ Slack webhook not set. Alert skipped."

    except Exception as e:
        return json.dumps({"error": f"Notifier error: {e}"})

notifier_tool = Tool(
    name="Notifier",
    func=notifier_agent,
    description="Send a Slack alert based on enriched log event context. Input should include username, IP, abuse score, and failure history."
)