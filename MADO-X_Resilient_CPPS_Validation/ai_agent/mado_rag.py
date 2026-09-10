import chromadb
from sentence_transformers import SentenceTransformer

# Initialize local ChromaDB client (persistent storage on disk)
chroma_client = chromadb.PersistentClient(path="./mado_chroma_db")
collection = chroma_client.get_or_create_collection(name="factory_downtime_logs")

# Load lightweight local embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Enhanced Seed historical downtime logs with quantitative success metrics
historical_logs = [
    "Case 1 (M5 Overload): Downstream buffer blockage on conveyor belt 3. Resolution: WIP gating + M5 speed boost. Metrics: Initial queue 28, recovery time 90 simulation steps, 2.24 kWh/part energy efficiency.",
    "Case 2 (M1 Overload): Thermal overload during startup. Resolution: Staggering injection with WIP gating. Metrics: Initial queue 18, recovery time 60 steps, zero inventory waste.",
    "Case 3 (M3 Breakdown): Sensor drift. Resolution: Optical sensor recalibration and speed modulation. Metrics: Queue reduced from 41 to <5 in 120 steps with a +14.1% throughput gain."
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
print("[RAG] ChromaDB successfully initialized with quantitative metrics and historical logs indexed.")

# Function to query historical root-cause and quantitative recovery advice
def query_factory_rag(query_text: str, n_results=1):
    query_embedding = embedding_model.encode([query_text]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results['documents'][0][0] if results['documents'] else "No historical record found."