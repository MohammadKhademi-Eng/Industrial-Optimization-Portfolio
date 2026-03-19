## 01 - MADO Framework Model Architecture

This folder provides the architectural specification for the **Maintenance-Aware Digital Twin (MADO)** developed in AnyLogic.

### **Logic Overview**
Due to the proprietary nature of the custom **Java classes** and sensitive industrial data integrated into the model, the raw `.alp` source file is restricted. However, full transparency of the system logic is provided through the following:

* **System Logic Flow**: Discrete Event Simulation (DES) synchronized with Agent-Based (ABM) triggers for maintenance events.
* **Decision Logic**: Stochastic resilience triggers based on real-time parameter drift (± 20%).
* **Optimization Integration**: Built-in connection to the **OptQuest** engine using Scatter Search and Tabu Search heuristics.

*Please refer to `MADO_Framework_Architecture.jpg` in this folder for a visual map of the model's agents, variables, and production flow logic.*
