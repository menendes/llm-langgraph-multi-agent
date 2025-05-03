from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Qdrant config
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "threat_docs"

# Qdrant client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Local embedding model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_index():
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=QDRANT_COLLECTION,
    )
    return VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)

# Main retrieval function
def retriever_agent(query: str) -> str:
    index = get_index()
    retriever = index.as_retriever(similarity_top_k=1)
    nodes = retriever.retrieve(query)

    if not nodes:
        return "No relevant documents found."

    return "\n\n".join([f"- {node.text.strip()}" for node in nodes])