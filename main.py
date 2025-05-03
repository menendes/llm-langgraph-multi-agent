from dotenv import load_dotenv

# Load environment variables
load_dotenv()



# Placeholder: we'll hook into LangGraph flow later
# def run_query(query: str):
#     print(f"🔍 Running query: {query}")
#     result = run_langgraph_pipeline(query)
#     print("\n🧠 Final Response:\n", result)
#     print("🚧 LangGraph flow integration coming soon...")
#
# if __name__ == "__main__":
#     # You can modify this query anytime to test different prompts
#     query = "Show me recent failed login attempts from suspicious IPs."
#     run_query(query)


# Test retriever agent only
from agents.retriever_agent import retriever_agent
if __name__ == "__main__":
    query = "Tell me about any activity from IP 203.0.113.50"
    print(f"Query: {query}")

    result = retriever_agent(query)
    print("\n Retriever Agent Result:\n")
    print(result)

# testing sql agent
# from agents.sql_agent import sql_agent
#
# if __name__ == "__main__":
#     query = "Show me recent failed login attempts from suspicious IPs."
#     print(f"🔍 Query: {query}")
#
#     result = sql_agent(query)
#     print("\n🗃️ SQL Agent Result:\n")
#     print(result)
