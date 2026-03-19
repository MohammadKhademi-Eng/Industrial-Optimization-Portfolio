## 02 - Optimization Traces & Performance Results

This folder contains the quantitative output data confirming the performance gains of the **MADO Framework**. These traces provide the evidence for the **+13.9% profit increase** and **+14.1% throughput improvement** reported in the study.

### **Contents:**
* **Baseline Traces**: Raw CSV output representing the "As-Is" system state without maintenance-aware optimization.
* **Optimization Scenarios (S1–S6)**: Results for six distinct operational scenarios, testing different maintenance thresholds and production speeds.
* **KPI Metrics**: Detailed breakdowns of Lead Time, Tardiness, OEE (Overall Equipment Effectiveness), and Energy Consumption.

### **Data Structure:**
* `run_summary.csv`: Aggregated performance metrics for each simulation run.
* `timeseries.csv`: Step-by-step temporal data showing system behavior under varying loads.
* `leadtime_samples.csv`: Distribution data for order fulfillment speeds.
