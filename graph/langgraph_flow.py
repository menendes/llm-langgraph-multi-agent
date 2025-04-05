from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.runnables import Runnable

# Agent stubs we'll implement later
from agents.sql_agent import sql_agent
from agents.retriever_agent import retriever_agent
from agents.web_agent import web_agent
from agents.synthesizer_agent import synthesizer_agent

# Define the shared state that passes between nodes
class AgentState(TypedDict):
    query: str
    sql_result: str
    retrieved_docs: str
    web_results: str
    final_response: str

# Step 1: Wrap each agent to follow the expected input/output format
def sql_node(state: AgentState) -> AgentState:
    result = sql_agent(state["query"])
    state["sql_result"] = result
    return state

def retriever_node(state: AgentState) -> AgentState:
    result = retriever_agent(state["query"])
    state["retrieved_docs"] = result
    return state

def web_node(state: AgentState) -> AgentState:
    result = web_agent(state["query"])
    state["web_results"] = result
    return state

def synthesizer_node(state: AgentState) -> AgentState:
    result = synthesizer_agent(state)
    state["final_response"] = result
    return state

# Step 2: Build the graph
graph = StateGraph(AgentState)

graph.add_node("sql_agent", sql_node)
graph.add_node("retriever_agent", retriever_node)
graph.add_node("web_agent", web_node)
graph.add_node("synthesizer", synthesizer_node)

# Step 3: Connect nodes
graph.set_entry_point("sql_agent")
graph.add_edge("sql_agent", "retriever_agent")
graph.add_edge("retriever_agent", "web_agent")
graph.add_edge("web_agent", "synthesizer")
graph.set_finish_point("synthesizer")

# Step 4: Export the runnable
runnable_graph: Runnable = graph.compile()

def run_langgraph_pipeline(query: str) -> str:
    initial_state = {"query": query}
    final_state = runnable_graph.invoke(initial_state)
    return final_state["final_response"]
