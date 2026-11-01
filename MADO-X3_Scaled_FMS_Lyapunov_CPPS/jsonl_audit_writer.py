# jsonl_audit_writer.py
import json
from datetime import datetime

AUDIT_LOG_FILE = "mado_x3_audit_log.jsonl"


def log_compliance_event(run_id: int, telemetry_status: str, recommendation: str, triggered_ai: bool,
                         cell_states: dict):
    """
    EU AI Act Articles 12 & 13 Compliance:
    Appends an immutable, run-indexed JSONL audit entry for automated record-keeping.
    """
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "run_id": run_id,
        "telemetry_status": telemetry_status,
        "cell_states": cell_states,
        "ai_intervention": triggered_ai,
        "recommendation": recommendation if recommendation else "Nominal state bypassed AI.",
        "regulatory_compliance": "EU AI Act Articles 12 & 13 - Automated Record-Keeping & Algorithmic Transparency"
    }

    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(audit_entry) + "\n")
    print(f"[AUDIT LOGGED] Immutable compliance record appended to {AUDIT_LOG_FILE}")