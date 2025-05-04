from langchain_openai import ChatOpenAI
from agents.log_monitor_agent import log_tool
from agents.threat_intel_agent import threat_tool
from agents.notifier_agent import notifier_tool
from agents.sql_lookup_agent import sql_tool
from agents.web_search_agent import web_search_tool
import os
from langgraph.prebuilt import create_react_agent
from langchain.agents import Tool


llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

all_tools: list[Tool]  = [
    log_tool,  # Analyze logs and identify suspicious behavior
    threat_tool,  # Check IP addresses against threat intelligence sources
    notifier_tool,  # Notify only if a threat or abnormal pattern is confirmed
    sql_tool,  # Lookup known history of users or IPs based on past log data
    web_search_tool,  # Search for unfamiliar terms or CVEs on the web
]

system_prompt = (
    "You are a cybersecurity assistant that receives structured JSON log events."
    " Use the available tools to analyze, enrich, and determine if an event is a real threat."
    " Only send a notification when there is sufficient evidence of suspicious behavior."
    " Use LogMonitor to evaluate logs, SQLLookup to examine failed history, ThreatIntel to assess IP reputation,"
    " WebSearch for extra context, and Notifier only when truly necessary."
    " Always include relevant information from previous tool results in the final Notifier input, such as abuse_score or fail counts."
    " Do not fabricate or omit known data. Do not make up input values."
)
langgraph_agent_executor  = create_react_agent(
    tools=all_tools,
    model=llm,
    prompt=system_prompt,
    debug=True
)