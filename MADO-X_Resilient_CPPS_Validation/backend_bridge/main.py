import os
import json
import threading
import time
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="MADO-X Sovereign Edge-AI Bridge",
    version="1.0.0",
    description="FastAPI backend bridging AnyLogic DES telemetry with empirical KPI tracking."
)

file_lock = threading.Lock()


class SimulationTelemetry(BaseModel):
    timestamp: float
    simulation_status: str = "RUNNING"
    run_id: int = 0
    throughput: int = 0
    oee: float = 94.2
    energy_intensity: float = 2.24
    profit: float = 0.0
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
    print(
        f"[TELEMETRY] Run:{data.run_id} | Time: {data.timestamp:5.1f} | "
        f"Throughput:{data.throughput} | OEE:{data.oee:.1f}% | "
        f"Energy:{data.energy_intensity:.2f} | Profit:${data.profit:.1f}"
    )

    bridge_path = "simulation_state.json"
    temp_path = "simulation_state_temp.json"

    with file_lock:
        try:
            with open(temp_path, "w") as f:
                json.dump(data.model_dump(), f, indent=4)

            success = False
            for attempt in range(5):
                try:
                    os.replace(temp_path, bridge_path)
                    success = True
                    break
                except PermissionError:
                    time.sleep(0.05)

            if not success:
                return {"status": "warning", "message": "File write deferred due to lock conflict."}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {"status": "success", "message": f"Run {data.run_id} synchronized."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)