import os
from dotenv import load_dotenv
from graph.langgraph_flow import run_langgraph_pipeline


# Load environment variables
load_dotenv()

# Placeholder: we'll hook into LangGraph flow later
def run_query(query: str):
    print(f"🔍 Running query: {query}")
    result = run_langgraph_pipeline(query)
    print("\n🧠 Final Response:\n", result)
    print("🚧 LangGraph flow integration coming soon...")

if __name__ == "__main__":
    # You can modify this query anytime to test different prompts
    query = "Show me recent failed login attempts from suspicious IPs."
    run_query(query)
