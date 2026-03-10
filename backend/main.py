"""
EDIPS — FastAPI Backend
========================
Serves patient risk scores, SHAP explanations, and live alerts
to the React frontend.

Run:
    cd backend
    uvicorn main:app --reload --port 8000

Endpoints:
    GET  /api/patients              → all ICU patients with scores
    GET  /api/patients/{id}         → single patient detail
    GET  /api/patients/{id}/shap    → SHAP feature explanations
    GET  /api/alerts                → active high-risk alerts
    GET  /api/metrics               → model performance metrics
    WS   /ws/live                   → WebSocket live score stream
"""

import json
import asyncio
import random
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from predict import build_patients, get_patient_shap, load_models

# ── App state ──────────────────────────────────────────────────────────────────

BASE = Path(__file__).parent.parent
METRICS_PATH = BASE / "metrics.json"

_models   = None
_patients = []     # in-memory patient list, refreshed on startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _models, _patients
    print("Loading models and patient data...")
    _models   = load_models()
    _patients = build_patients(_models)
    print(f"Loaded {len(_patients)} ICU patients.")
    yield


app = FastAPI(title="EDIPS API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper ─────────────────────────────────────────────────────────────────────

def _generate_alerts(patients):
    """Derive alerts from patients with high risk scores."""
    INFECTION_INFO = {
        "vap":    ("VAP",    "Ventilator-Associated Pneumonia"),
        "clabsi": ("CLABSI", "Central Line Bloodstream Infection"),
        "cauti":  ("CAUTI",  "Urinary Tract Infection"),
    }
    DEVICE_KEYS = {"vap": "vent", "clabsi": "cvc", "cauti": "cath"}

    alerts = []
    alert_id = 1
    for p in patients:
        for inf_key, (label, _) in INFECTION_INFO.items():
            score = p["scores"][inf_key]
            device_active = p["devices"].get(DEVICE_KEYS[inf_key], False)
            if score >= 0.6 and device_active:
                level = "RED" if score >= 0.75 else "AMBER"
                alerts.append({
                    "id":          f"A{alert_id:03d}",
                    "patientId":   p["id"],
                    "type":        label,
                    "level":       level,
                    "time":        f"{random.randint(2, 120)} min ago",
                    "score":       score,
                    "explanation": _alert_explanation(p, inf_key),
                    "acked":       False,
                })
                alert_id += 1
    return alerts


def _alert_explanation(patient, inf_type):
    v = patient["vitals"]
    d = patient["devices"]
    if inf_type == "vap":
        return (f"Ventilator day {patient['dayInICU']}, SpO₂ {v['spo2']}%, "
                f"RR {v['rr']} bpm, Temp {v['temp']}°C")
    if inf_type == "clabsi":
        return (f"CVC dwell {d['cvcHours']:.0f}h, "
                f"Temp {v['temp']}°C, HR {v['hr']} bpm")
    return (f"Catheter {d['cathHours']:.0f}h, "
            f"Temp {v['temp']}°C, RR {v['rr']} bpm")


# ── REST endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/patients")
def get_patients():
    return _patients


@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: str):
    for p in _patients:
        if p["id"] == patient_id:
            return p
    raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/api/patients/{patient_id}/shap")
def get_shap(patient_id: str):
    for p in _patients:
        if p["id"] != patient_id:
            continue
        shap_data = get_patient_shap(_models, patient_id)
        if shap_data is None:
            raise HTTPException(status_code=404, detail="SHAP data not found")
        return shap_data
    raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/api/alerts")
def get_alerts():
    return _generate_alerts(_patients)


@app.get("/api/metrics")
def get_metrics():
    if METRICS_PATH.exists():
        with open(METRICS_PATH) as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="metrics.json not found")


@app.get("/health")
def health():
    return {"status": "ok", "patients_loaded": len(_patients)}


# ── WebSocket live stream ──────────────────────────────────────────────────────

@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send small score drift updates every 4 seconds
            updates = []
            for p in _patients:
                updates.append({
                    "id": p["id"],
                    "scores": {
                        k: round(min(0.99, max(0.01,
                            p["scores"][k] + (random.random() - 0.47) * 0.012)), 2)
                        for k in ("vap", "clabsi", "cauti", "combined")
                    }
                })
            await websocket.send_text(json.dumps({"type": "score_update", "data": updates}))
            await asyncio.sleep(4)
    except WebSocketDisconnect:
        pass
