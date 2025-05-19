"""
Dynamic LLM‑directed multi‑agent threat‑detection pipeline (v4)
--------------------------------------------------------------
**Change‑log**
~~~~~~~~~~~~~
* **notify** tool signature expanded → now accepts the raw *event* plus all
  individual scores, so the Slack alert lists *exact* numbers (risk_score,
  abuse_score, previous_incidents, final_score).
* **System prompt** updated so the LLM knows to pass those fields when it calls
  *notify*.
* Code otherwise unchanged: conditional enrichment and routing logic stay the
  same.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain.schema import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict


# ---------------------------------------------------------------------------
# 1. Event schema (typing helper – the LLM just receives a JSON blob)
# ---------------------------------------------------------------------------
class Event(TypedDict):
    timestamp: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    http_status: int
    url: str
    method: str
    user_agent: str
    threat_signature: str
    bytes_sent: int
    bytes_received: int

# ---------------------------------------------------------------------------
# 2. Agent tool implementations (stateless functions)
# ---------------------------------------------------------------------------
@tool
def event_analysis(event: Event) -> Dict[str, int]:
    """Analyse the log event and return a base *risk_score* (0‑100)."""
    score = 0
    if event["http_status"] in {401, 403}:
        score += 25
    if event["threat_signature"]:
        score += 40
    if event["method"] not in {"GET", "HEAD"}:
        score += 10
    if event["bytes_received"] == 0:
        score += 5
    return {"risk_score": score}


@tool
def sql_lookup(ip: str) -> Dict[str, int]:
    """Return *previous_incidents* count for the given IP (mocked)."""
    return {"previous_incidents": 3 if ip == "203.0.113.45" else 0}


@tool
def threat_intel(ip: str) -> Dict[str, int]:
    """Fetch *abuse_score* (0‑100) from CTI feed (mocked)."""
    return {"abuse_score": 80 if ip == "203.0.113.45" else 10}


@tool
def aggregate_risk(risk_score: int, abuse_score: int = 0, previous_incidents: int = 0) -> Dict[str, int]:
    """Combine partial scores into **final_score**.

    Formula: `risk_score + abuse_score + (20 if previous_incidents > 0)`.
    Missing inputs default to 0 so the LLM can skip enrichment when the risk is low.
    """
    final = risk_score + abuse_score + (20 if previous_incidents > 0 else 0)
    return {"final_score": final}


@tool
def web_search(query: str) -> Dict[str, List[str]]:
    """Return a handful of URLs for the query (via DuckDuckGo)."""
    ddg = DuckDuckGoSearchRun()
    hits = ddg.run(query, max_results=5)
    if isinstance(hits, str):
        hits = hits.split("\n")[:5]
    return {"web_hits": hits}


@tool
def notify(event: Event, risk_score: int, abuse_score: int = 0, previous_incidents: int = 0, final_score: int = 0) -> Dict[str, str]:
    """Send a Slack alert summarising *all* scores.

    Parameters
    ----------
    event : Event           – the original log event
    risk_score : int        – output from *event_analysis*
    abuse_score : int       – from *threat_intel* (optional)
    previous_incidents: int – from *sql_lookup* (optional)
    final_score : int       – from *aggregate_risk*
    """
    hook = os.getenv("SLACK_WEBHOOK_URL")
    if not hook:
        return {"status": "skipped – webhook not configured"}

    import requests, textwrap

    text = textwrap.dedent(
        f"""
        *THREAT ALERT*  (final_score {final_score})
        ──────────────────────────────────────────
        • risk_score: {risk_score}
        • abuse_score: {abuse_score}
        • previous_incidents: {previous_incidents}
        
        ```json
        {json.dumps(event, indent=2)}
        ```
        """
    )
    requests.post(hook, json={"text": text}).raise_for_status()
    return {"status": "sent"}

# ---------------------------------------------------------------------------
# 3. Bind tools to GPT‑4o and create **supervisor node**
# ---------------------------------------------------------------------------
TOOLS = [event_analysis, sql_lookup, threat_intel, aggregate_risk, web_search, notify]

system_prompt = SystemMessage(
    content=(
        "You are a cybersecurity orchestrator. The user will send one log event in JSON.\n\n"
        "Workflow guidance:\n"
        "• Always start with *event_analysis* (pass the full event).\n"
        "• If `risk_score` is **below 30**, you may skip further enrichment and just call *aggregate_risk* (with default 0s) followed by a final summary.\n"
        "• If `risk_score` is **30 or higher**, optionally call *sql_lookup*, *threat_intel*, and/or *web_search* to enrich context.\n"
        "• When you have enough data, call *aggregate_risk*.\n"
        "• If `final_score` is **80 or above**, call *notify* and include: event, risk_score, abuse_score (if any), previous_incidents (if any), final_score.\n"
        "• Finish with a short plain‑English explanation of your decision (no tool calls)."
    )
)

supervisor_llm = ChatOpenAI(model="gpt-4", temperature=0).bind_tools(TOOLS)


def supervisor_node(state: MessagesState) -> MessagesState:
    response: BaseMessage = supervisor_llm.invoke(state["messages"])
    state["messages"].append(response)
    return state

# ---------------------------------------------------------------------------
# 4. Dynamic LangGraph workflow (unchanged)
# ---------------------------------------------------------------------------
graph = StateGraph(MessagesState)

graph.add_node("supervisor", supervisor_node)
graph.add_node("tool_node", ToolNode(TOOLS))

graph.set_entry_point("supervisor")


def route(state: MessagesState):
    last: BaseMessage = state["messages"][-1]
    return "tool_node" if getattr(last, "additional_kwargs", {}).get("tool_calls") else END

graph.add_conditional_edges("supervisor", route)
graph.add_edge("tool_node", "supervisor")

app = graph.compile()

# ---------------------------------------------------------------------------
# 5. Quick CLI test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_event: Event = {
        "timestamp": "2025-05-18T13:25:00Z",
        "src_ip": "203.0.113.45",
        "dst_ip": "10.20.30.40",
        "src_port": 443,
        "dst_port": 3355,
        "protocol": "HTTPS",
        "http_status": 401,
        "url": "/login",
        "method": "POST",
        "user_agent": "curl/8.2.1",
        "threat_signature": "Brute_force_login",
        "bytes_sent": 512,
        "bytes_received": 0,
    }

    messages = [
        system_prompt,
        HumanMessage(content="NEW_EVENT:\n```json\n" + json.dumps(sample_event) + "\n```"),
    ]

    final_state = app.invoke({"messages": messages})

    print("\n=== TRANSCRIPT ===")
    for msg in final_state["messages"]:
        print(f"[{msg.type}] {msg.content}")
