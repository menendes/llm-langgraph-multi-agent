import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from qdrant_client import QdrantClient, models

load_dotenv()

# === Paths ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DOCS_FOLDER = os.path.join(BASE_DIR, "data", "threat_docs")

# === Qdrant Config ===
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "threat_docs"

# Local embedding model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def load_docs_to_qdrant():
    print("Loading documents from:", DOCS_FOLDER)
    documents = SimpleDirectoryReader(DOCS_FOLDER).load_data()

    print("Connecting to Qdrant...")
    if qdrant_client.collection_exists(QDRANT_COLLECTION):
        qdrant_client.delete_collection(QDRANT_COLLECTION)

    print(f"Creating collection `{QDRANT_COLLECTION}` in Qdrant...")
    qdrant_client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=QDRANT_COLLECTION)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Embedding with MiniLM and indexing...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model
    )
    print("Finished indexing to Qdrant.")

    count = qdrant_client.count(collection_name=QDRANT_COLLECTION, exact=True).count
    print(f"{count} documents embedded and stored in Qdrant.")

if __name__ == "__main__":
    load_docs_to_qdrant()
