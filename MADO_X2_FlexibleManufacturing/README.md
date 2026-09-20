# MADO-X2: Sovereign, Zero-Trust Neuro-Symbolic Edge-AI Framework for Flexible Manufacturing

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Compliance: EU AI Act](https://img.shields.io/badge/EU_AI_Act-Articles_12%2C_13%2C_14-blue)](https://artificialintelligenceact.eu/)

## Overview
**MADO-X2** is a sovereign, zero-trust, offline-first neuro-symbolic edge-AI architecture designed for closed-loop discrete-event simulation (DES) control and real-time industrial resilience in Industry 5.0 manufacturing lines. 

This repository houses the core control scripts, communication bridges, and execution logs demonstrating live closed-loop anomaly detection and automated recovery.

---

## System Architecture & Tech Stack

* **Physical Simulation Layer:** AnyLogic 8.9 (Multi-agent discrete-event simulation tracking SMT workstation queues, AGV transport, and reflow oven bottlenecks).
* **Inter-Process Communication (IPC):** FastAPI asynchronous backend providing thread-safe locking and atomic 1.0s state synchronization (`brain_bridge.py`).
* **Supervisory Intelligence:** LangGraph 4-node state graph orchestrating anomaly detection, ChromaDB RAG historical retrieval, and local neural inference.
* **Edge Reasoning:** Local offline Ollama / Llama 3 8B INT4 inference running at zero-shot capacity with temperature = 0.0 (zero cloud telemetry dependencies).
* **Regulatory Compliance:** Built-in alignment with the **2026 EU AI Act** via automated run-indexed immutable JSONL audit trails (Articles 12 & 13) and Human-in-the-Loop operator verification gates (Article 14).

---

## Demonstration Workflow (4-Phase Cycle)

The system executes a fully automated closed-loop recovery sequence during bottleneck violations:

1. **Phase 1: Real-Time Telemetry Ingestion**
   * FastAPI synchronizes live AnyLogic simulation state variables across the IPC bridge at 1.0s intervals.
2. **Phase 2: Offline RAG Diagnosis**
   * Local Llama 3 (Ollama) queries ChromaDB historical metrics when a threshold violation is detected (`Q_oven >= 5`).
3. **Phase 3: EU AI Act Art. 14 HITL Authorization & Actuation**
   * Execution pauses for safety compliance. Upon operator verification (`y`), the system executes a 4x speed boost coupled with upstream WIP gating to drain the buffer.
4. **Phase 4: Autonomous Hysteresis Reset**
   * Once the queue clears ($\le 3$), the system autonomously resets to nominal flow, logging an immutable audit record (`Incident #1 Resolved`).

---

## Repository Structure

```text
MADO_X2_FlexibleManufacturing/
├── src/
│   ├── LangGraph_Supervisory_Agent.py
│   └── FastAPI_Bridge.py
├── config/
│   └── control_command.json
└── audit_logs/
    └── execution_audit.jsonl
