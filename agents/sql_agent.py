from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
import os

# Setup OpenAI
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

# Connect to local SQLite database
db_path = os.path.join(os.path.dirname(__file__), "../data/logs.db")
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# Create the LangChain SQL agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

def sql_agent(natural_language_query: str) -> str:
    try:
        response = sql_agent_executor.run(natural_language_query)
        return response
    except SQLAlchemyError as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Agent error: {e}"