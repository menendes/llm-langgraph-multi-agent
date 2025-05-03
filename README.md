# llm-langgraph-multi-agent
Building a LangGraph-powered multi-agent system that answers cyber threat questions 


###
conda create -n llm-multiagent python=3.10
conda activate conda create -n llm-multiagent

'''
cyber-agent-orchestrator/
├── agents/
│   ├── sql_agent.py                # Placeholder for SQL query agent
│   ├── retriever_agent.py          # Uses Qdrant + LlamaIndex
│   ├── web_agent.py                # Uses Tavily or SerpAPI
│   └── synthesizer_agent.py        # Compiles and summarizes context
├── graph/
│   └── langgraph_flow.py           # Orchestration logic (LangGraph DAG)
├── data/
│   ├── logs.db                     # You can add SQLite mock data here
│   └── threat_docs/                # For internal reports, PDFs, etc.
├── tools/
│   ├── qdrant_loader.py            # For indexing threat_docs to Qdrant
│   └── web_search_tool.py          # Wraps Tavily search
├── main.py                         # CLI entry point
├── .env                            # API keys
├── README.md                       # Project overview
└── requirements.txt                # Dependencies


'''


docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v $(pwd)/data/qdrant_storage:/qdrant/storage qdrant/qdrant

