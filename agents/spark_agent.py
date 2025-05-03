import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from pyspark.sql import SparkSession

# === Initialize Spark session ===
spark = SparkSession.builder.appName("CyberLogAnalyzer").getOrCreate()

# === Load logs CSV into Spark DataFrame ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_FILE = os.path.join(BASE_DIR, "data", "logs_large.csv")
df = spark.read.csv(LOG_FILE, header=True, inferSchema=True)
df.createOrReplaceTempView("logs")  # now accessible as SQL table 'logs'

# === Setup OpenAI LLM ===
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

# === Define the Spark SQL execution tool ===
def run_spark_query(query: str) -> str:
    try:
        result = spark.sql(query).toPandas().to_markdown(index=False)
        return result
    except Exception as e:
        return f"[Spark SQL Error] {e}"

spark_tool = Tool(
    name="spark_sql",
    func=run_spark_query,
    description="Use this to run SQL queries on logs"
)

# === Build the agent using LangChain ===
agent_executor = initialize_agent(
    tools=[spark_tool],
    llm=llm,
    verbose=True,
)

# === Public interface ===
def spark_agent(query: str) -> str:
    try:
        return agent_executor.run(query)
    except Exception as e:
        return f"[SparkAgent Error] {e}"