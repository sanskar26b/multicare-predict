# EDIPS — Equipment-Device Integrated Prediction System

> **ICU Infection Risk Prediction** | VAP · CLABSI · CAUTI
> VIT Pune · CS-AIML-A · Group SY A-10 · Guide: Prof. Amruta Bhawarthi

---

## What is EDIPS?

EDIPS is a clinical decision-support system that predicts the risk of three life-threatening **ICU-acquired infections** 24–48 hours before onset:

| Infection | Full Name | Linked Device |
|---|---|---|
| **VAP** | Ventilator-Associated Pneumonia | Mechanical Ventilator |
| **CLABSI** | Central Line-Associated Bloodstream Infection | Central Venous Catheter |
| **CAUTI** | Catheter-Associated Urinary Tract Infection | Urinary Catheter |

The system processes real MIMIC-IV clinical data, runs risk models per patient, explains predictions with SHAP feature importance, and streams live risk scores to a clinical dashboard via WebSocket.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         EDIPS SYSTEM                              │
│                                                                    │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────────┐   │
│  │ Dataset  │──▶│   XAI    │──▶│  Model   │──▶│   Backend   │   │
│  │ MIMIC-IV │   │ EDA +    │   │ LR / RF  │   │  FastAPI    │   │
│  │ 100 pts  │   │ Preproc  │   │  / MLP   │   │  REST + WS  │   │
│  └──────────┘   └──────────┘   └──────────┘   └──────┬──────┘   │
│                                                        │          │
│                                              ┌─────────▼────────┐ │
│                                              │    Frontend      │ │
│                                              │ React 18 + Vite  │ │
│                                              │  Live Dashboard  │ │
│                                              └──────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**Data flow:**
Raw MIMIC-IV CSVs → Feature Engineering → Model Training → FastAPI serves predictions + SHAP → React dashboard displays live risk scores

---

## Repository Structure

```
multicare-predict/
│
├── README.md                        ← You are here
├── readme_dataset.md                ← Full MIMIC-IV dataset documentation
├── run_pipeline.py                  ← Root orchestrator (run everything from here)
│
├── prepare_training_data.py         ← Raw CSVs → training_ready/training_set.csv
├── train_pipeline.py                ← Trains LR, RF, MLP models
├── best_model_sklearn.pkl           ← Saved models + scaler (all 3)
├── best_model.pt                    ← MLP checkpoint
├── metrics.json                     ← Model performance metrics
├── evaluation_results.txt           ← Detailed evaluation report
├── feature_importance.png           ← RF top-15 feature importance plot
├── training_plot.png                ← MLP loss/accuracy curves
│
├── backend/                         ← FastAPI REST + WebSocket server
│   ├── main.py                      ← App entry point, routes, WebSocket
│   ├── predict.py                   ← Patient builder, scoring engine, SHAP
│   ├── requirements.txt             ← Python dependencies
│   └── venv/                        ← Isolated Python 3.11 virtual environment
│
├── frontend/                        ← React 18 + Vite clinical dashboard
│   ├── EDIPS_Dashboard.jsx          ← Main app (live API fetch + WebSocket)
│   ├── main.jsx                     ← React entry point
│   ├── index.html                   ← HTML shell
│   ├── vite.config.js               ← Vite config + /api and /ws proxy
│   ├── mockData.js                  ← Fallback demo data (offline mode)
│   ├── utils.js                     ← Risk color/label helpers
│   ├── package.json
│   └── components/
│       ├── PatientCard.jsx          ← Patient summary card
│       ├── PatientDetail.jsx        ← Full patient detail view
│       ├── SHAPPanel.jsx            ← SHAP explainability panel (live API)
│       ├── ScoreGauge.jsx           ← Circular risk gauge (VAP/CLABSI/CAUTI)
│       ├── TrajectoryChart.jsx      ← 72h risk trajectory chart
│       ├── VitalsStrip.jsx          ← Real-time vitals strip
│       ├── AlertCard.jsx            ← Individual alert card
│       ├── AlertsSidebar.jsx        ← Sliding alerts drawer
│       ├── StatsBar.jsx             ← Top stats (total, high-risk, alert count)
│       ├── LiveTicker.jsx           ← Live timestamp ticker
│       ├── SynergyIndicator.jsx     ← Multi-device compound risk indicator
│       ├── DeviceBadge.jsx          ← Device on/off + dwell time badge
│       └── indicators.jsx           ← RiskPill components
│
├── xai/                             ← Preprocessing + Explainable AI pipeline
│   ├── README.md
│   ├── requirements.txt
│   ├── preprocessing/
│   │   ├── config.py                ← Paths, window size (24h), IQR threshold
│   │   ├── eda.py                   ← EDA: missing values heatmap, distributions
│   │   ├── preprocess.py            ← Mean/ffill imputation, IQR clip, StandardScaler
│   │   └── create_windows.py        ← Sliding window generator → shape (N, 24, features)
│   ├── scripts/
│   │   └── run_pipeline.py          ← EDA → preprocess → windows (full pipeline)
│   ├── data/processed/
│   │   └── X.npy                    ← Pre-built windowed ML input array
│   └── reports/                     ← EDA summary txt, missing values heatmap, distributions
│
├── training_ready/                  ← ML-ready datasets
│   ├── training_set.csv             ← 275 rows × 32 features (numeric only)
│   └── admissions_merged.csv        ← Full merged dataset (55 columns, used by backend)
│
├── training_data_source/            ← 15 raw source CSVs for prepare_training_data.py
├── hosp/                            ← Full MIMIC-IV hospital tables (22 CSVs)
└── icu/                             ← Full MIMIC-IV ICU tables (9 CSVs)
```

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| ML Models | scikit-learn | 1.8.0 |
| Explainability | SHAP (TreeExplainer) | 0.51.0 |
| Backend framework | FastAPI + Uvicorn | 0.135 / 0.41 |
| Real-time | WebSocket (native FastAPI) | — |
| Frontend | React + Vite + Recharts | 18 / 5 / 2 |
| Data processing | pandas + numpy | 3.0 / 2.4 |
| Dataset | MIMIC-IV Demo v2.2 | — |
| Python | CPython | 3.11 |
| Node | Node.js | 18+ |

---

## Setup

### Prerequisites

- Python 3.9 or higher (3.11 recommended)
- Node.js 18+ and npm
- ~500 MB free disk space

### 1. Clone

```bash
git clone https://github.com/your-org/multicare-predict.git
cd multicare-predict
```

### 2. Backend — create virtual environment and install deps

```bash
cd backend

# Create the venv
python -m venv venv

# Activate
venv\Scripts\activate        # Windows CMD / PowerShell
# source venv/bin/activate   # macOS / Linux

# Install
pip install -r requirements.txt
```

Packages installed: `fastapi`, `uvicorn[standard]`, `pandas`, `numpy`, `scikit-learn`, `shap`

### 3. Frontend — install Node dependencies

```bash
cd frontend
npm install
```

---

## Running the System

Open **two terminals** from the repo root.

### Terminal 1 — Backend

```bash
cd backend
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

uvicorn main:app --reload --port 8000
```

Expected output:
```
Loading models and patient data...
Loaded 128 ICU patients.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

---

### Using the pipeline orchestrator

The `run_pipeline.py` script at the repo root wraps all steps:

```bash
# Run data prep + training (steps 1–3, one time):
python run_pipeline.py

# Individual steps:
python run_pipeline.py --step prepare    # Raw CSVs → training_set.csv
python run_pipeline.py --step xai        # EDA + preprocess + windows
python run_pipeline.py --step train      # Train LR/RF/MLP models
python run_pipeline.py --step backend    # Start FastAPI on :8000
python run_pipeline.py --step frontend   # Start Vite on :5173
```

---

## API Reference

Base URL: `http://localhost:8000`

### REST Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/patients` | All ICU patients with VAP / CLABSI / CAUTI scores |
| `GET` | `/api/patients/{id}` | Single patient with full detail |
| `GET` | `/api/patients/{id}/shap` | SHAP feature importances per infection type |
| `GET` | `/api/alerts` | Active alerts (score ≥ 0.6 with active device) |
| `GET` | `/api/metrics` | Model performance metrics |
| `GET` | `/health` | Health check |

### WebSocket

| Path | Description |
|---|---|
| `WS /ws/live` | Pushes `score_update` events every 4 seconds |

### Patient object schema

```json
{
  "id": "ICU-10004235",
  "age": 47,
  "gender": "M",
  "unit": "MICU",
  "dayInICU": 5,
  "devices": {
    "vent": true,  "ventHours": 89.1,
    "cvc": true,   "cvcHours": 118.9,
    "cath": true,  "cathHours": 118.9
  },
  "scores": {
    "vap": 0.43, "clabsi": 0.43, "cauti": 0.40, "combined": 0.43
  },
  "vitals": {
    "hr": 113, "temp": 37.0, "spo2": 96, "rr": 22, "bp": "108/68"
  },
  "trend": "stable",
  "base_risk": 0.234
}
```

### SHAP response schema

```json
{
  "vap": [
    { "label": "Heart Rate",          "value": "113",      "shap": 0.1469, "dir": "up" },
    { "label": "Respiratory Rate",    "value": "22",       "shap": 0.0972, "dir": "up" },
    { "label": "ICU Length of Stay",  "value": "5.0 days", "shap": 0.0800, "dir": "up" }
  ],
  "clabsi": [ ... ],
  "cauti":  [ ... ]
}
```

---

## Model Performance

**Dataset:** MIMIC-IV Demo v2.2 — 275 admissions, 100 patients
**Target:** In-hospital mortality (binary, proxy for critical illness)
**Split:** 70% train / 15% val / 15% test · Stratified

| Model | AUROC | AUPRC | F1 | Accuracy |
|---|---|---|---|---|
| **Logistic Regression** ★ | **0.9250** | 0.3333 | 0.3333 | 0.9048 |
| Random Forest | 0.8500 | 0.2000 | 0.0000 | 0.9048 |
| MLP Neural Network | 0.6250 | 0.1357 | 0.0000 | 0.9524 |

★ Best by AUROC — used for infection risk scoring in production.

**32 input features:**

| Category | Features |
|---|---|
| Labs | glucose, creatinine, WBC, BUN, hemoglobin, platelet, potassium, sodium |
| Vitals | heart rate, systolic BP, diastolic BP, respiratory rate, SpO₂, temperature |
| ICU | total ICU stays, total ICU LOS |
| Stay | LOS hours/days, ED wait time, admit hour, day of week, weekend flag |
| Counts | diagnoses, procedures, unique drugs |
| Demographics | age, gender, race, insurance, admission type (all encoded) |

**Infection score formula:**

```
base = mortality_probability × 1.2
vap    = base × (1 + min(vent_hours / 336, 1.0) × 2.0)   if ventilated
clabsi = base × (1 + min(cvc_hours  / 336, 1.0) × 1.5)   if has CVC
cauti  = base × (1 + min(cath_hours / 336, 1.0) × 1.2)   if has catheter
```

---

## XAI Pipeline

Located in `xai/`. Can run independently of the rest of the system.

```
training_ready/training_set.csv
        │
        ▼
    eda.py              Generates:
                        ├── reports/eda_summary.txt
                        ├── reports/missing_values.png
                        └── reports/feature_distributions.png
        │
        ▼
    preprocess.py       Steps:
                        ├── Missing values: mean imputation + forward fill
                        ├── Outlier clipping: IQR method (threshold = 1.5)
                        └── Scaling: StandardScaler (fit on train only)
        │
        ▼
    create_windows.py   Sliding windows:
                        └── Output shape: (N, 24, 32) → data/processed/X.npy
```

```bash
cd xai
python scripts/run_pipeline.py
```

---

## Re-training from Scratch

```bash
# 1. Build ML dataset from raw MIMIC-IV CSVs
python prepare_training_data.py
# → training_ready/training_set.csv
# → training_ready/admissions_merged.csv

# 2. Run XAI preprocessing
cd xai && python scripts/run_pipeline.py && cd ..
# → xai/data/processed/X.npy

# 3. Train all three models
python train_pipeline.py
# → best_model_sklearn.pkl
# → best_model.pt
# → metrics.json, evaluation_results.txt
# → feature_importance.png, training_plot.png
```

---

## Dashboard Features

| Feature | Description |
|---|---|
| Live patient grid | 128 ICU patients sorted by combined risk score |
| Real-time scores | WebSocket pushes score drift every 4 seconds |
| Filter bar | Filter by risk level, ventilated / CVC / catheter |
| Stats bar | Totals: patients, high-risk count, active alerts |
| Patient detail | VAP/CLABSI/CAUTI gauges, device dwell time, vitals strip, 72h trajectory, SHAP panel |
| SHAP panel | Live per-patient feature importances with directional bars |
| Alerts drawer | RED/AMBER alerts with one-click acknowledge |
| Offline mode | Falls back to demo mock data if backend is unreachable |

---

## Dataset

**MIMIC-IV Clinical Database Demo v2.2**
Source: [PhysioNet](https://doi.org/10.13026/dp1f-ex47) — Beth Israel Deaconess Medical Center

| Metric | Value |
|---|---|
| Patients | 100 de-identified |
| Hospital admissions | 275 |
| ICU stays | 140 |
| ICU patients used by backend | 128 |
| Lab results | 107,727 rows |
| ICU chart events | 668,862 rows |
| Unique lab test types | 498 |
| Unique ICU chart items | 1,318 |

All dates are shifted into the future for de-identification. Free-text notes are excluded. See `readme_dataset.md` for the full table-by-table reference.

**License:** [PhysioNet Credentialed Health Data License 1.5.0](https://physionet.org/content/mimiciv-demo/view-license/2.2/)

---

## Team

| Role | Member |
|---|---|
| Data Lead | Yash |
| Backend Lead | Deep |
| Frontend Lead | Sanskar |
| Project Guide | Prof. Amruta Bhawarthi |

**Institution:** VIT Pune · Department of CS-AIML · Group SY A-10

---

## Citation

> Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023).
> MIMIC-IV Clinical Database Demo (version 2.2). PhysioNet.
> https://doi.org/10.13026/dp1f-ex47
