import chromadb
from sentence_transformers import SentenceTransformer

# Initialize local ChromaDB client (persistent storage on disk)
chroma_client = chromadb.PersistentClient(path="./mado_chroma_db")
collection = chroma_client.get_or_create_collection(name="factory_downtime_logs")

# Load lightweight local embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Seed historical downtime logs & resolutions
historical_logs = [
    "Machine M5 queue overflow caused by downstream buffer blockage on conveyor belt 3. Resolved by clearing jammed pallets and re-routing flow.",
    "Machine M1 thermal overload due to high friction during startup phase. Resolved by staggering part injection rates using WIP gating.",
    "Machine M3 frequent breakdowns from sensor drift. Resolved by recalibrating optical proximity sensors and updating maintenance intervals."
]

ids = ["log_1", "log_2", "log_3"]

# Embed and add documents to ChromaDB collection if empty
if collection.count() == 0:
    embeddings = embedding_model.encode(historical_logs).tolist()
    collection.add(
        documents=historical_logs,
        embeddings=embeddings,
        ids=ids
    )
print("[RAG] ChromaDB successfully initialized and historical logs indexed.")

# Function to query historical root-cause advice
def query_factory_rag(query_text: str, n_results=1):
    query_embedding = embedding_model.encode([query_text]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results['documents'][0][0] if results['documents'] else "No historical record found."