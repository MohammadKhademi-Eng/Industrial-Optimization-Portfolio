import chromadb
from sentence_transformers import SentenceTransformer

chroma_client = chromadb.PersistentClient(path="./mado_chroma_db")
collection = chroma_client.get_or_create_collection(name="jobshop_recovery_logs")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

historical_logs = [
    "Case 1 (Thermal Oven Bottleneck): Reflow oven accumulation queue reached 26 boards due to dual SMT line convergence. Resolution: SPEED_BOOST actuation (halved curing cycle) combined with WIP gating on Cell A and B. Metrics: Queue cleared to <=4 in 75 seconds, zero defective solder joints.",
    "Case 2 (AGV Fleet Deadlock): Transporters choked at cross-aisle intersection. Resolution: Dynamic fleet rerouting and free-space boundary expansion. Metrics: Idle AGV availability restored to 2 within 40 seconds.",
    "Case 3 (SMT Cell A Backlog): Component reel jam on pick-and-place nozzle. Resolution: Inflow gating on Cell A with load balancing to Cell B. Metrics: Work-in-progress reduced by 65% with +18.2% total line throughput."
]

ids = ["log_reflow_oven", "log_agv_fleet", "log_smt_feeder"]

if collection.count() == 0:
    embeddings = embedding_model.encode(historical_logs).tolist()
    collection.add(
        documents=historical_logs,
        embeddings=embeddings,
        ids=ids
    )
print("[RAG] ChromaDB initialized: Multi-Cell SMT & AGV recovery cases indexed.")

def query_factory_rag(query_text: str, n_results=1):
    query_embedding = embedding_model.encode([query_text]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results['documents'][0][0] if results['documents'] else "No historical record found."