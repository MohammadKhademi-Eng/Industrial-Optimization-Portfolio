import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import json
import time
import requests
from datetime import datetime
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from mado_rag import query_factory_rag


class MadoState(TypedDict):
    telemetry_status: str
    recommendation: str
    requires_ai_intervention: bool
    cell_states: dict
    simulation_status: str
    run_id: int


OLLAMA_URL = "http://localhost:11434/api/generate"
TELEMETRY_FILE = "simulation_state.json"
CONTROL_COMMAND_FILE = "control_command.json"

# State tracking for multi-wave industrial latching
active_mitigation_in_progress = False
last_anomaly_signature = ""
incident_cycle_count = 0


def log_compliance_event(run_id: int, telemetry_status: str, recommendation: str, triggered_ai: bool):
    audit_file = f"mado_x2_audit_log_run_{run_id}.jsonl"
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "run_id": run_id,
        "telemetry_status": telemetry_status,
        "ai_intervention": triggered_ai,
        "recommendation": recommendation if recommendation else "Nominal state bypassed AI.",
        "regulatory_compliance": "EU AI Act Articles 12 & 13 - Automated Record-Keeping & Algorithmic Transparency"
    }
    with open(audit_file, "a") as f:
        f.write(json.dumps(audit_entry) + "\n")


def check_factory_node(state: MadoState) -> MadoState:
    global active_mitigation_in_progress, last_anomaly_signature, incident_cycle_count

    cell_data = {}
    current_run_id = 1
    sim_status = "RUNNING"

    try:
        if os.path.exists(TELEMETRY_FILE):
            with open(TELEMETRY_FILE, "r") as f:
                d = json.load(f)
                current_run_id = d.get("run_id", 1)
                sim_status = d.get("simulation_status", "RUNNING")
                cell_data = {
                    "Cell_A_Queue": d.get("q_A", 0),
                    "Cell_B_Queue": d.get("q_B", 0),
                    "Oven_Queue": d.get("q_oven", 0),
                    "Oven_Utilization": d.get("u_oven", 0.0),
                    "AGV_Idle": d.get("agv_idle", 0)
                }
    except Exception as e:
        print(f"[WARNING] Telemetry read error: {e}")

    oven_q = cell_data.get("Oven_Queue", 0)
    agv_idle = cell_data.get("AGV_Idle", 0)
    q_a = cell_data.get("Cell_A_Queue", 0)
    q_b = cell_data.get("Cell_B_Queue", 0)

    # 1. Recovery Check: Reset latch completely when oven buffer clears to default baseline
    if active_mitigation_in_progress and oven_q <= 3:
        active_mitigation_in_progress = False
        last_anomaly_signature = ""
        incident_cycle_count += 1
        print(
            f"\n>>> [LANGGRAPH MONITOR] Buffer Cleared (Q={oven_q} <= 3). Incident #{incident_cycle_count} Resolved. Resuming Default Nominal Supervision.\n")

    # 2. Calibrated Anomaly Detection
    current_anomalies = []

    # Primary Bottleneck: Reflow Oven accumulation queue
    if oven_q >= 5:
        current_anomalies.append("REFLOW_OVEN_OVERLOAD")

    # Secondary Bottleneck: Severe AGV Transport Starvation (both cells congested)
    if agv_idle == 0 and (q_a >= 12 or q_b >= 12):
        current_anomalies.append("AGV_STARVATION")

    current_signature = "+".join(sorted(current_anomalies))

    requires_ai = False
    if not current_anomalies:
        status = "NOMINAL: Factory flow stable across cells and buffer."
    else:
        if active_mitigation_in_progress:
            # Check for new compound failures emerging while mitigating primary
            if current_signature != last_anomaly_signature and last_anomaly_signature != "":
                requires_ai = True
                status = f"CRITICAL: New compound anomaly detected: {current_signature}"
                last_anomaly_signature = current_signature
            else:
                status = f"MITIGATING: Prior actuation active. Draining buffer (Q={oven_q})."
                requires_ai = False
        else:
            requires_ai = True
            status = f"ALARMING: {', '.join(current_anomalies)} (Oven Q={oven_q}, AGV Idle={agv_idle})"
            last_anomaly_signature = current_signature

    return {
        "telemetry_status": status,
        "requires_ai_intervention": requires_ai,
        "recommendation": "",
        "cell_states": cell_data,
        "simulation_status": sim_status,
        "run_id": current_run_id
    }


def llama3_reasoning_node(state: MadoState) -> MadoState:
    print(f"\n[LANGGRAPH] Anomaly detected! Querying ChromaDB RAG & Local Llama 3...")
    historical_context = query_factory_rag(state["telemetry_status"])

    status = state["telemetry_status"]
    if "REFLOW_OVEN_OVERLOAD" in status:
        task_instruction = "Recommend SPEED_BOOST on the Reflow Oven and temporary WIP gating on upstream cells under 20 words."
    else:
        task_instruction = "Recommend AGV fleet dynamic rerouting and buffer relief under 20 words."

    prompt = (
        f"Smart Factory Anomaly: {state['telemetry_status']}.\n"
        f"Live Facility State: {json.dumps(state['cell_states'], indent=2)}\n"
        f"Historical Retrieval Context: {historical_context}\n"
        f"Task: {task_instruction}"
    )

    payload = {"model": "llama3:latest", "prompt": prompt, "stream": False}

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=45)
        rec = response.json().get("response",
                                  "").strip() if response.status_code == 200 else "Execute SPEED_BOOST on Reflow Oven with upstream WIP Gating."
    except Exception:
        rec = "Execute SPEED_BOOST on Reflow Oven with upstream WIP Gating."

    return {
        "telemetry_status": state["telemetry_status"],
        "requires_ai_intervention": state["requires_ai_intervention"],
        "recommendation": rec,
        "cell_states": state["cell_states"],
        "simulation_status": state["simulation_status"],
        "run_id": state["run_id"]
    }


def hitl_operator_gate(state: MadoState) -> MadoState:
    global active_mitigation_in_progress
    print("\n" + "=" * 65)
    print(f"[HITL GATE - EU AI ACT ART. 14] OPERATOR OVERSIGHT PAUSE")
    print(f"Telemetry: {state['telemetry_status']}")
    print(f"Mitigation Strategy: {state['recommendation']}")
    print("=" * 65)

    approval = input("Authorize autonomous line actuation (SPEED_BOOST + WIP Gating)? (y/n): ").strip().lower()

    if approval == "y":
        print("[HITL GATE] Verified by Operator. Dispatching control_command.json...")
        control_payload = {
            "action": "SPEED_BOOST",
            "target": "reflowOven",
            "speed_boost": True,
            "gate_upstream": True,
            "timestamp": time.time()
        }
        with open(CONTROL_COMMAND_FILE, "w") as f:
            json.dump(control_payload, f, indent=4)

        active_mitigation_in_progress = True
        print("[ACTUATION] Actuation file written. Active mitigation engaged.")
    else:
        print("[HITL GATE] Rejected by operator. No physical line change executed.")
        active_mitigation_in_progress = False
        state["recommendation"] = "REJECTED BY OPERATOR: " + state["recommendation"]

    return state


def edge_actuation_node(state: MadoState) -> MadoState:
    log_compliance_event(
        run_id=state["run_id"],
        telemetry_status=state["telemetry_status"],
        recommendation=state["recommendation"],
        triggered_ai=state["requires_ai_intervention"]
    )
    return state


def route_decision(state: MadoState) -> Literal["llama3_reasoning_node", "edge_actuation_node"]:
    if state["requires_ai_intervention"]:
        return "llama3_reasoning_node"
    return "edge_actuation_node"


workflow = StateGraph(MadoState)
workflow.add_node("check_factory_node", check_factory_node)
workflow.add_node("llama3_reasoning_node", llama3_reasoning_node)
workflow.add_node("hitl_operator_gate", hitl_operator_gate)
workflow.add_node("edge_actuation_node", edge_actuation_node)

workflow.set_entry_point("check_factory_node")
workflow.add_conditional_edges("check_factory_node", route_decision, {
    "llama3_reasoning_node": "llama3_reasoning_node",
    "edge_actuation_node": "edge_actuation_node"
})
workflow.add_edge("llama3_reasoning_node", "hitl_operator_gate")
workflow.add_edge("hitl_operator_gate", "edge_actuation_node")
workflow.add_edge("edge_actuation_node", END)

checkpointer = MemorySaver()
compiled_app = workflow.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    print("--- MADO-X2 Supervisory Multi-Agent Active ---")
    last_mod_time = 0.0
    iteration_counter = 0

    while True:
        try:
            if os.path.exists(TELEMETRY_FILE):
                mtime = os.path.getmtime(TELEMETRY_FILE)
                if mtime != last_mod_time:
                    last_mod_time = mtime
                    iteration_counter += 1

                    thread_tag = f"cycle_{incident_cycle_count}_tick_{iteration_counter}"
                    config = {"configurable": {"thread_id": thread_tag}}

                    initial_state = {
                        "telemetry_status": "",
                        "recommendation": "",
                        "requires_ai_intervention": False,
                        "cell_states": {},
                        "simulation_status": "RUNNING",
                        "run_id": 1
                    }
                    compiled_app.invoke(initial_state, config=config)
        except Exception as e:
            print(f"[LOOP ERROR] {e}")

        time.sleep(1.0)