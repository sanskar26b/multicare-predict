# EDIPS – Equipment Device Integrated Prediction System

## Project Overview
This repository contains the preprocessing pipeline for the **EDIPS** project. The goal is to build a robust system for infection prediction using ICU patient data from the MIMIC-IV Clinical Database Demo 2.2.

## Role
**Preprocessing and Explainable AI Lead**

## Dataset Explanation
The pipeline uses the MIMIC-IV Clinical Database Demo, focusing on:
- **hosp/**: Hospital-wide clinical tables (admissions, lab results, prescriptions).
- **icu/**: ICU monitoring data (vitals, fluid input/output).
- **training_ready/**: Pre-merged datasets for ML pipeline development.

## Preprocessing Pipeline
The workflow follows these steps:
1. **Raw ICU Tables**: Initial data collection.
2. **Training Pipeline**: Generation of `training_set.csv`.
3. **EDA**: Statistical analysis and visualization of `training_set.csv`.
4. **Preprocessing**: Handling missing values, outlier detection, and feature scaling.
5. **Sliding Windows**: Converting tabular data into 24-hour time-series sequences.
6. **ML Input**: Numpy arrays (`X.npy`) ready for model training.

### Workflow Diagram
```mermaid
graph TD
    A[Raw ICU Tables] --> B[Training Pipeline]
    B --> C[training_set.csv]
    C --> D[EDA]
    D --> E[Preprocessing]
    E --> F[Sliding Windows]
    F --> G[ML Input (X.npy)]
```

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the complete pipeline:
   ```bash
    python scripts/run_pipeline.py
    ```

## Detailed File Structure & Justification

### 📂 `data/`
*   **`raw/`**: Intended for the 31 original MIMIC-IV demo tables (e.g., `patients.csv`, `chartevents.csv`). 
    *   *Justification*: Keeps source data separate from processed artifacts to ensure data integrity and prevent accidental modification of clinical records.
*   **`training_ready/`**: Contains `training_set.csv`.
    *   *Justification*: This is the boundary between Data Engineering and Data Science. My work begins here to maintain modularity, allowing the preprocessing module to function independently of the upstream database merging logic.
*   **`processed/`**: Contains `processed_data.csv` and `X.npy`.
    *   *Justification*: Stores the final, model-ready outputs. Segregating these ensures that the feature scaling and sliding window operations don't overwrite the source training data.

### 📂 `preprocessing/`
*   **`config.py`**: Centralized configuration for all paths, window sizes (24), and thresholds.
    *   *Justification*: Hard-coding paths is a primary source of failure in ML pipelines. This file provides a single source of truth for the entire repository.
*   **`eda.py`**: Automated statistical analysis and visualization.
    *   *Justification*: Crucial for identifying data drift and missingness patterns before modeling. Automated report generation ensures consistency across different data versions.
*   **`preprocess.py`**: Core cleaning logic (IQR Outlier clipping, Mean/FFill imputation, Z-score scaling).
    *   *Justification*: Implements the medical-standard preprocessing requirements. Modularizing this allows for easy testing of different imputation strategies.
*   **`create_windows.py`**: Logic for converting tabular data into 3D Numpy arrays `(N, 24, features)`.
    *   *Justification*: Necessary for time-series modeling (e.g., LSTM/RNN). It transforms raw patient observations into temporal sequences that capture the progression of a patient’s ICU stay.

### 📂 `scripts/`
*   **`run_pipeline.py`**: The main entry point that orchestrates EDA, Preprocessing, and Windowing.
    *   *Justification*: Simplifies reproducibility. A single command guarantees that the entire pipeline is executed in the correct dependency order.

### 📂 `reports/`
*   *Justification*: Provides a non-technical summary (text and images) of the dataset state, essential for mid-semester reviews and "Explainable AI" reporting, as requested in the project lead role.
