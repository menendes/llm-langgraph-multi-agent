from typing import Annotated
from langgraph.prebuilt import InjectedState
from langchain.agents import Tool
import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# SQLLookup Tool
# Purpose: Count historical failed login attempts by username and/or IP from local SQLite DB
# Input: JSON string with at least "ip_address" and/or "username"
# Output: JSON string with fail count for each identifier

db_path = os.path.join(os.path.dirname(__file__), "../data/logs.db")

def sql_lookup_agent(state: Annotated[dict, InjectedState]) -> str:
    try:
        if isinstance(state, str):
            event = json.loads(state)
        else:
            return json.dumps({"error": "Invalid input format"})

        ip = event.get("ip_address")
        username = event.get("username")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        response = {}

        if ip:
            cursor.execute("SELECT COUNT(*) FROM logs WHERE ip_address = ? AND success = 0", (ip,))
            response["ip_fail_count"] = cursor.fetchone()[0]

        if username:
            cursor.execute("SELECT COUNT(*) FROM logs WHERE username = ? AND success = 0", (username,))
            response["user_fail_count"] = cursor.fetchone()[0]

        conn.close()
        return json.dumps(response)

    except Exception as e:
        return json.dumps({"error": f"SQLLookup error: {e}"})

sql_tool = Tool(
    name="SQLLookup",
    func=sql_lookup_agent,
    description=(
        "Look up historical failed login counts for a given IP or username from the logs database. "
        "Input must be a JSON object with at least 'ip_address' and 'username'."
    )
)