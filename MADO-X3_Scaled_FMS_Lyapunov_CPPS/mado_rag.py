# mado_rag.py
import os
import chromadb
from chromadb.utils import embedding_functions


def query_factory_rag(query_text: str) -> str:
    """Queries persistent ChromaDB vector store for historical recovery metrics."""
    db_path = "./mado_chroma_db"
    os.makedirs(db_path, exist_ok=True)

    client = chromadb.PersistentClient(path=db_path)

    # Use lightweight sentence-transformer embedding default
    ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(name="factory_recovery_traces", embedding_function=ef)

    # If collection is empty, seed it with baseline historical recovery knowledge
    if collection.count() == 0:
        collection.add(
            documents=[
                "Reflow oven overload (Q >= 5): Execute speed boost to 1.5x and engage upstream WIP gating to reduce queue drift.",
                "Workstation A queue spike: Throttle buffer injection rate and verify AGV availability."
            ],
            metadatas=[{"source": "historical_run_1"}, {"source": "historical_run_2"}],
            ids=["trace_1", "trace_2"]
        )

    results = collection.query(query_texts=[query_text], n_results=1)
    if results and results['documents']:
        return results['documents'][0][0]
    return "Standard industrial recovery trace: Throttle upstream injection and double bottleneck service rate."