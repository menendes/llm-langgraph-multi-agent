from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
import os

# Folder where your internal docs live (use .md, .txt, .pdf etc.)
DOCS_FOLDER = os.path.join(os.path.dirname(__file__), "../data/threat_docs")

# Qdrant config
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "threat_docs"

# Qdrant client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Load or create vector index
def get_index():
    try:
        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(storage_context)
    except:
        docs = SimpleDirectoryReader(DOCS_FOLDER).load_data()
        vector_store = QdrantVectorStore(client=qdrant_client, collection_name=QDRANT_COLLECTION)
        storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir="./storage")
        index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
        index.storage_context.persist()
    return index

# Main retrieval function
def retriever_agent(query: str) -> str:
    index = get_index()
    retriever = index.as_retriever(similarity_top_k=3)
    nodes = retriever.retrieve(query)
    return "\n\n".join([node.text for node in nodes])