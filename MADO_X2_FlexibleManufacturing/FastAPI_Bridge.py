import os
import json
import threading
import time
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="MADO-X2 Sovereign Multi-Cell Edge Bridge",
    version="2.0.0",
    description="FastAPI backend bridging AnyLogic Job-Shop telemetry with LangGraph."
)

file_lock = threading.Lock()

# Matches the exact JSON structure sent by telemetryEvent in AnyLogic
class JobShopTelemetry(BaseModel):
    timestamp: float
    q_A: int
    q_B: int
    q_oven: int
    u_oven: float
    agv_idle: int
    simulation_status: str = "RUNNING"
    run_id: int = 1

@app.get("/")
def read_root():
    return {"status": "online", "framework": "MADO-X2 Sovereign Edge-AI"}

# Dual-route binding ensures both /telemetry and /api/telemetry succeed
@app.post("/telemetry")
@app.post("/api/telemetry")
def receive_telemetry(data: JobShopTelemetry):
    print(
        f"[TELEMETRY] Time: {data.timestamp:5.1f}s | "
        f"Cell_A Q: {data.q_A:2d} | Cell_B Q: {data.q_B:2d} | "
        f"Oven Q: {data.q_oven:2d} | Oven Util: {data.u_oven:.2f} | AGV Idle: {data.agv_idle}"
    )

    bridge_path = "simulation_state.json"
    temp_path = "simulation_state_temp.json"

    with file_lock:
        try:
            with open(temp_path, "w") as f:
                json.dump(data.model_dump(), f, indent=4)

            success = False
            for _ in range(5):
                try:
                    os.replace(temp_path, bridge_path)
                    success = True
                    break
                except PermissionError:
                    time.sleep(0.02)

            if not success:
                return {"status": "warning", "message": "Lock conflict"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {"status": "success", "received_at": data.timestamp}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)