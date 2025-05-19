import json
from typing import List
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode

from events_feed import event_stream
from tools.event_analysis import event_analysis
from tools.notifier import notify
from tools.sql_lookup import sql_lookup
from tools.threat_intel import threat_intel
from tools.web_search import web_search

TOOLS = [event_analysis, sql_lookup, threat_intel, web_search, notify]

SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are a cybersecurity orchestrator with five tools:\n"
        "• *event_analysis(event)* – always run first and inspect 'risk_score'.\n"
        "• *sql_lookup(ip, username?)* – login-history stats for context.\n"
        "• *threat_intel(ip)* – AbuseIPDB reputation for the IP.\n"
        "• *web_search(ip?, abuse_score?, threat_signature?, cve_ids?)* – "
        "gather public references (returns ip_hits / pattern_hits / cve_hits).\n"
        "• *notify(summary, risk, src_ip, links?)* – send the final Slack/console alert. Use **once** at the very end.\n\n"
        "Workflow:\n"
        "1. Call *event_analysis* with the raw event JSON.\n"
        "2. If risk_score ≥ 30, consider calling *sql_lookup* (ip/username) for recent failures.\n"
        "3. If abuse_score is unknown and risk_score ≥ 30, call *threat_intel*.\n"
        "4. If abuse_score ≥ 50 or threat_signature is present, call *web_search* with "
        "appropriate parameters (include abuse_score so the tool knows whether to do IP look-up).\n"
        "5. If overall threat is high (risk ≥ 80 OR abuse_score ≥ 75 OR ip_fail ≥ 5), "
        "call *notify* with a <5-line summary, the risk score, the src_ip, and up to 3 informative links.\n"
        "6. End with a short plain-English assessment. Avoid duplicate tool calls."
    )
)

LLM = ChatOpenAI(model="gpt-4", temperature=0).bind_tools(TOOLS)

def supervisor(state: MessagesState) -> MessagesState:
    resp: BaseMessage = LLM.invoke(state["messages"])
    state["messages"].append(resp)
    return state

G = StateGraph(MessagesState)
G.add_node("supervisor", supervisor)
G.add_node("tool", ToolNode(TOOLS))
G.set_entry_point("supervisor")
G.add_conditional_edges("supervisor", lambda s: "tool" if getattr(s["messages"][-1],"additional_kwargs",{}).get("tool_calls") else END)
G.add_edge("tool","supervisor")
APP = G.compile()

if __name__ == "__main__":
    for idx, evt in enumerate(event_stream(limit=1), 1):
        print(f"\n===== EVENT {idx} =====")
        msgs: List[BaseMessage] = [SYSTEM_PROMPT, HumanMessage(content="EVENT:\n```json\n"+json.dumps(evt)+"\n```")]
        end_state = APP.invoke({"messages": msgs})
        for m in end_state["messages"]:
            role = m.type.ljust(6)
            print(f"[{role}] {m.content}")