from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Load OpenAI LLM
llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

def synthesizer_agent(state: dict) -> str:
    query = state.get("query", "")
    sql_result = state.get("sql_result", "No SQL results.")
    retrieved_docs = state.get("retrieved_docs", "No internal documents found.")
    web_results = state.get("web_results", "No web results found.")

    prompt = f"""
You are a cybersecurity assistant. A user asked:

"{query}"

Here is what you found:
- 🗃️ SQL data: {sql_result}
- 📄 Internal documents: {retrieved_docs}
- 🌐 Web results: {web_results}

Now, write a concise and helpful report combining all this information.
If some sources are missing, just work with what you have.
"""

    response = llm.invoke(prompt)
    return response.content.strip()
