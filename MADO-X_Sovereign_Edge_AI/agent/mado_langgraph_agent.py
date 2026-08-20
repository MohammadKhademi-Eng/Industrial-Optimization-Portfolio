import os
import json
import time
import requests
from datetime import datetime
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import RAG retrieval utility from mado_rag.py
from mado_rag import query_factory_rag


# Define the shared state structure for the factory agent
class MadoState(TypedDict):
    telemetry_status: str
    recommendation: str
    requires_ai_intervention: bool
    machine_states: dict
    simulation_status: str


OLLAMA_URL = "http://localhost:11434/api/generate"
TELEMETRY_FILE = "simulation_state.json"
AUDIT_LOG_FILE = "mado_audit_log.jsonl"

# --- Cooldown Tracking Variables (EU AI Act Ergonomics) ---
last_alarm_signature = ""
last_alarm_timestamp = 0.0
COOLDOWN_WINDOW = 900.0  # 15 minutes in seconds


# --- EU AI Act Immutable Audit Logger Utility ---
def log_compliance_event(telemetry_status: str, recommendation: str, triggered_ai: bool):
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "telemetry_status": telemetry_status,
        "ai_intervention": triggered_ai,
        "recommendation": recommendation if recommendation else "N/A - Nominal state bypassed AI.",
        "regulatory_compliance": "EU AI Act Articles 12 & 13 - Automated Record-Keeping & Algorithmic Transparency"
    }
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(audit_entry) + "\n")


# Node 1: Check Live Factory Telemetry Matrix across M1-M5 with Fixed ID-Only Cooldown
def check_factory_node(state: MadoState) -> MadoState:
    global last_alarm_signature, last_alarm_timestamp
    print("\n[LANGGRAPH] Assessing multi-machine factory telemetry matrix (M1-M5)...")

    # Staleness check for AnyLogic shutdown
    try:
        if os.path.exists(TELEMETRY_FILE):
            file_mod_time = os.path.getmtime(TELEMETRY_FILE)
            if time.time() - file_mod_time > 45:
                print("[LANGGRAPH] Telemetry stream stopped. AnyLogic simulation ended.")
                return {
                    "telemetry_status": "FINISHED",
                    "requires_ai_intervention": False,
                    "recommendation": "Simulation telemetry timed out.",
                    "machine_states": {},
                    "simulation_status": "FINISHED"
                }
    except Exception as e:
        print(f"[WARNING] Staleness check error: {e}")

    machines = {}
    alarming_ids = []
    alarming_details = []
    sim_status = "RUNNING"

    try:
        if os.path.exists(TELEMETRY_FILE):
            with open(TELEMETRY_FILE, "r") as f:
                data = json.load(f)
                sim_status = data.get("simulation_status", "RUNNING")
                for i in range(1, 6):
                    machines[f"M{i}"] = {
                        "queue": data.get(f"m{i}_queue", 0),
                        "utilization": data.get(f"m{i}_utilization", 0.0)
                    }
    except Exception as e:
        print(f"[WARNING] Could not read telemetry file: {e}")

    if sim_status == "FINISHED":
        return {
            "telemetry_status": "FINISHED",
            "requires_ai_intervention": False,
            "recommendation": "Simulation completed successfully.",
            "machine_states": machines,
            "simulation_status": "FINISHED"
        }

    for m_id, metrics in machines.items():
        if metrics["queue"] > 5 and metrics["utilization"] >= 0.95:
            alarming_ids.append(m_id)  # Used for pure ID-based cooldown checking
            alarming_details.append(f"{m_id} (Queue: {metrics['queue']}, Util: {metrics['utilization']})")

    current_time = time.time()

    if alarming_details:
        status = f"ALARMING - Cascading bottlenecks detected on: {', '.join(alarming_details)}"

        # Create signature strictly from machine IDs (e.g., "M5"), ignoring queue numbers
        alarm_signature = ", ".join(sorted(alarming_ids))

        # Apply 15-minute cooldown window based strictly on machine IDs
        if alarm_signature == last_alarm_signature and (current_time - last_alarm_timestamp) < COOLDOWN_WINDOW:
            requires_ai = False
            status += " [COOLDOWN ACTIVE: Suppressing prompt]"
        else:
            requires_ai = True
            last_alarm_signature = alarm_signature
            last_alarm_timestamp = current_time
    else:
        status = "NOMINAL: Multi-stage CPPS flow stable across M1-M5."
        requires_ai = False
        last_alarm_signature = ""

    return {
        "telemetry_status": status,
        "requires_ai_intervention": requires_ai,
        "recommendation": "",
        "machine_states": machines,
        "simulation_status": "RUNNING"
    }


# Node 2: Local Llama 3 Regulatory Reasoning with ChromaDB RAG Integration
def phi3_reasoning_node(state: MadoState) -> MadoState:
    print("[LANGGRAPH] Anomaly detected! Querying ChromaDB RAG & local Llama 3...")

    # Query ChromaDB vector database for historical downtime logs
    historical_context = query_factory_rag(state['telemetry_status'])

    # Enrich prompt with RAG retrieval context
    prompt = (
        f"Factory anomaly: {state['telemetry_status']}.\n"
        f"Historical Context: {historical_context}\n"
        f"Give a 1-sentence mitigation strategy under 20 words for EU AI Act compliance."
    )

    # Use llama:latest which is robustly configured in your local Ollama environment
    payload = {
        "model": "llama3:latest",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            rec = response.json().get("response", "").strip()
        else:
            # Capture the exact error payload text from Ollama server for deep debugging
            rec = f"Ollama Error [{response.status_code}]: {response.text}"
    except Exception as e:
        rec = f"Error connecting to local LLM: {str(e)}"

    return {
        "telemetry_status": state["telemetry_status"],
        "requires_ai_intervention": state["requires_ai_intervention"],
        "recommendation": rec,
        "machine_states": state["machine_states"],
        "simulation_status": state["simulation_status"]
    }


# Node 3: Human-in-the-Loop (HITL) Operator Approval Gate (EU AI Act Article 14)
def hitl_operator_gate(state: MadoState) -> MadoState:
    print("\n" + "=" * 60)
    print("[HITL GATE] SYSTEM PAUSED FOR OPERATOR VERIFICATION (EU AI Act Art. 14)")
    print(f"Telemetry: {state['telemetry_status']}")
    print(f"AI Recommendation: {state['recommendation']}")
    print("=" * 60)

    approval = input("Do you authorize this edge intervention? Type 'y' or 'n': ").strip().lower()

    if approval == 'y':
        print("[HITL GATE] Operator approval granted. Proceeding to edge actuation.")
    else:
        print("[HITL GATE] Intervention rejected by operator. Bypassing execution.")
        state['recommendation'] = "REJECTED BY OPERATOR: " + state['recommendation']

    return state


# Node 4: Edge Actuation & Compliance Logging
def edge_actuation_node(state: MadoState) -> MadoState:
    if state["simulation_status"] == "FINISHED":
        return state

    print("[LANGGRAPH] Node 4: Executing sovereign edge actuation & logging audit trail...")

    log_compliance_event(
        telemetry_status=state["telemetry_status"],
        recommendation=state["recommendation"],
        triggered_ai=state["requires_ai_intervention"]
    )

    print(f"[AUDIT LOG] Successfully recorded decision to {AUDIT_LOG_FILE}")
    return state


# Conditional Routing Logic
def route_decision(state: MadoState) -> Literal["phi3_reasoning_node", "edge_actuation_node"]:
    if state["simulation_status"] == "FINISHED":
        return "edge_actuation_node"
    if state["requires_ai_intervention"]:
        return "phi3_reasoning_node"
    else:
        print("[LANGGRAPH] Status is NOMINAL. Bypassing LLM compute overhead.")
        return "edge_actuation_node"


# Build the LangGraph StateGraph Architecture with Memory Checkpointer
workflow = StateGraph(MadoState)

workflow.add_node("check_factory_node", check_factory_node)
workflow.add_node("phi3_reasoning_node", phi3_reasoning_node)
workflow.add_node("hitl_operator_gate", hitl_operator_gate)
workflow.add_node("edge_actuation_node", edge_actuation_node)

workflow.set_entry_point("check_factory_node")

workflow.add_conditional_edges(
    "check_factory_node",
    route_decision,
    {
        "phi3_reasoning_node": "phi3_reasoning_node",
        "edge_actuation_node": "edge_actuation_node"
    }
)

workflow.add_edge("phi3_reasoning_node", "hitl_operator_gate")
workflow.add_edge("hitl_operator_gate", "edge_actuation_node")
workflow.add_edge("edge_actuation_node", END)

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer, interrupt_before=["hitl_operator_gate"])

if __name__ == "__main__":
    print("--- MADO-X Continuous Multi-Machine Supervisory Agent Started ---")
    print("Monitoring live simulation telemetry matrix across M1-M5 with RAG...")

    config = {"configurable": {"thread_id": "mado_factory_thread_1"}}

    while True:
        try:
            initial_state = {
                "telemetry_status": "",
                "recommendation": "",
                "requires_ai_intervention": False,
                "machine_states": {},
                "simulation_status": "RUNNING"
            }

            result = app.invoke(initial_state, config=config)

            if result.get("simulation_status") == "FINISHED":
                print("\n[LANGGRAPH] Simulation finished flag received. Terminating agent loop gracefully.")
                print("--- MADO-X Supervisory Agent Closed Successfully ---")
                break

            snapshot = app.get_state(config)
            if snapshot.next and "hitl_operator_gate" in snapshot.next:
                app.invoke(None, config=config)

            print("-" * 60)
        except Exception as e:
            print(f"[RUNTIME ERROR] {e}")

        time.sleep(15)