## 03 - Verification Samples (Statistical Validation)

This folder contains the verification datasets used to ensure the statistical significance of the reported results. Every scenario (S1–S6) underwent a **Monte Carlo simulation** with **N=30 replications** to account for stochastic variance in machine failures and repair times.

### **Validation Methodology:**
* **Sample Size**: 30 independent replications per scenario.
* **Stochastic Variables**: MTTF (Mean Time To Failures) and MTTR (Mean Time To Repair) modeled using exponential and triangular distributions.
* **Objective**: To verify that the +13.9% profit increase is robust across different random seeds and is not an outlier.

### **Folder Structure:**
* Each `.zip` file contains the raw trace for 30 iterations of a specific scenario.
* These samples are provided for researchers wishing to conduct independent ANOVA or t-test validations on the MADO framework's performance.
