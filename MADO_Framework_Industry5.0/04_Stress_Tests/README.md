## 04 - Stress Tests & Stochastic Resilience

This folder contains the datasets for the **Stochastic Resilience** analysis of the MADO framework. These tests utilize **Freeform Monte Carlo** simulations to evaluate system stability under significant parameter variations.

### **Stress Test Methodology:**
* **Parameter Variation**: Critical system variables were varied using a Monte Carlo approach to simulate real-world uncertainty and "Parameter Drift."
* **Stochastic Robustness**: The goal was to verify if the optimized maintenance policy remains effective when the Mean Time To Failures (MTTF) and Mean Time To Repair (MTTR) deviate from their expected values.
* **Objective**: To quantify the framework's resilience and identify the boundaries where the +13.9% profit margin remains stable.

### **Contents:**
* `Parameter_Variation_Monte_Carlo_Stress_Tests.zip`: Contains raw temporal traces and performance CSVs (OEE, Lead Time, Downtime) for the varied parameter runs.
