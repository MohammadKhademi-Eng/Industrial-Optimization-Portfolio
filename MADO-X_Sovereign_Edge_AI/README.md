# MADO-X: Sovereign Edge-AI & Agentic Framework for Industry 5.0

## Overview
MADO-X is a dual-loop, neuro-symbolic edge-AI architecture designed for resilient cyber-physical production systems (CPPS). It bridges AnyLogic Discrete Event Simulation (DES) with local Small Language Models (SLMs) to ensure zero-trust automation and strict compliance with the **2026 EU AI Act (Articles 12, 13, & 14)**.

## Core Architecture
* **Fast-Loop (Deterministic Actuation):** Sub-10ms Java logic injection within AnyLogic to manage local machine queues and state tracking.
* **Slow-Loop (Sovereign LLM Orchestration):** FastAPI backend paired with LangGraph and a local instance of Llama 3 (via Ollama) for real-time root-cause analysis and RAG-augmented mitigation strategies.
* **Regulatory Governance:** Immutable compliance logging (`mado_audit_log.jsonl`) and mandatory Human-in-the-Loop (HITL) operator verification gates.

## Directory Structure
* `/backend/` $\rightarrow$ Concurrency-safe FastAPI application with atomic file swapping (`os.replace`).
* `/agent/` $\rightarrow$ LangGraph state supervisor and ChromaDB + sentence-transformers RAG vector pipeline.
* `/compliance/` $\rightarrow$ Tamper-evident audit logs demonstrating automated record-keeping.