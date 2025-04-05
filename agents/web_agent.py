import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Setup Tavily
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_agent(query: str) -> str:
    try:
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=3  # You can tweak this
        )
        results = response.get("results", [])
        if not results:
            return "No relevant web results found."

        # Build a summary from top results
        summary = ""
        for res in results:
            summary += f"- {res.get('title')}\n  {res.get('url')}\n  {res.get('content')[:200]}...\n\n"
        return summary.strip()

    except Exception as e:
        return f"Web agent error: {e}"
