import json

from langchain_core.messages import HumanMessage

from orchestrator.pipeline_executor import langgraph_agent_executor
from tools.kafka_simulator import get_sample_events

def start_watchdog():
    for event in get_sample_events():
        print("\nNew Event:", event)
        langgraph_agent_executor.invoke({
            "messages": [HumanMessage(content=json.dumps(event))]
        })
