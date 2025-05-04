from langchain.agents import Tool
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults

search_tool = DuckDuckGoSearchResults()

# WebSearch Tool
# Purpose: Search the web for supporting intelligence such as suspicious terms, attacker tools, or CVE IDs
# Input: plain text query (e.g. "brute force login", "CVE-2024-xyz")
# Output: plain text with summarized search result titles/snippets
web_search_tool = Tool(
    name="WebSearch",
    func=search_tool.run,
    description="Search the web for supporting context around suspicious keywords, IP usage, or attack terms. Input should be a plain string."
)
