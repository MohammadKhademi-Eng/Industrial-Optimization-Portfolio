import os
import json
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="MADO-X Sovereign Edge-AI Bridge",
    version="1.0.0",
    description="FastAPI backend bridging AnyLogic DES telemetry with clean console logging."
)


class SimulationTelemetry(BaseModel):
    timestamp: float
    simulation_status: str = "RUNNING"
    m1_queue: int
    m1_utilization: float
    m2_queue: int
    m2_utilization: float
    m3_queue: int
    m3_utilization: float
    m4_queue: int
    m4_utilization: float
    m5_queue: int
    m5_utilization: float


@app.get("/")
def read_root():
    return {"status": "online", "framework": "MADO-X Sovereign Edge-AI"}


@app.post("/api/telemetry")
def receive_telemetry(data: SimulationTelemetry):
    # Clean telemetry print format matching your desired output
    print(
        f"[TELEMETRY] Time: {data.timestamp:5.1f} | Status: {data.simulation_status} | "
        f"M1(Q:{data.m1_queue}, U:{data.m1_utilization:.2f}) | "
        f"M2(Q:{data.m2_queue}, U:{data.m2_utilization:.2f}) | "
        f"M3(Q:{data.m3_queue}, U:{data.m3_utilization:.2f}) | "
        f"M4(Q:{data.m4_queue}, U:{data.m4_utilization:.2f}) | "
        f"M5(Q:{data.m5_queue}, U:{data.m5_utilization:.2f})"
    )

    bridge_path = "simulation_state.json"
    temp_path = "simulation_state_temp.json"

    # Concurrency-safe atomic write pattern
    with open(temp_path, "w") as f:
        json.dump(data.model_dump(), f, indent=4)
    os.replace(temp_path, bridge_path)

    return {"status": "success", "message": "Multi-machine atomic telemetry logged and synchronized."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)