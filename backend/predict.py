"""
EDIPS — Patient Prediction Engine
==================================
Loads trained sklearn models, reads MIMIC-IV ICU patients, computes
VAP / CLABSI / CAUTI infection-risk scores, and returns structured patient
objects ready for the REST API and frontend.

Score derivation
----------------
  1. Base mortality risk  → LR model (AUROC 0.925) on 32 clinical features
  2. Device presence      → derived from ICU LOS + vitals heuristics
  3. Infection scores     → base_risk × device-duration multiplier per infection
  4. SHAP explanations    → RF TreeExplainer; falls back to RF importances
"""

import os
import pickle
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH   = os.path.join(BASE, "best_model_sklearn.pkl")
MERGED_PATH  = os.path.join(BASE, "training_ready", "admissions_merged.csv")

# ── Feature columns expected by the model (same as train_pipeline.py) ─────────
FEATURE_COLS = [
    "anchor_age", "los_hours", "los_days", "ed_wait_hours", "age_at_admission",
    "admit_hour", "admit_dayofweek", "is_weekend_admit",
    "num_diagnoses", "num_unique_diagnoses", "num_procedures",
    "lab_bun_last", "lab_creatinine_last", "lab_glucose_last",
    "lab_hemoglobin_last", "lab_platelet_last", "lab_potassium_last",
    "lab_sodium_last", "lab_wbc_last",
    "total_icu_stays", "total_icu_los",
    "vital_dia_bp_mean", "vital_heart_rate_mean", "vital_resp_rate_mean",
    "vital_spo2_mean", "vital_sys_bp_mean", "vital_temp_c_mean",
    "num_unique_drugs",
    "admission_type_encoded", "insurance_encoded", "gender_encoded", "race_encoded",
]

# Human-readable labels for the SHAP panel
FEATURE_LABELS = {
    "anchor_age":             "Patient Age",
    "los_hours":              "Hospital LOS (hrs)",
    "los_days":               "Hospital LOS (days)",
    "ed_wait_hours":          "ED Wait Time (hrs)",
    "age_at_admission":       "Age at Admission",
    "admit_hour":             "Admission Hour",
    "admit_dayofweek":        "Day of Week",
    "is_weekend_admit":       "Weekend Admission",
    "num_diagnoses":          "Total Diagnoses",
    "num_unique_diagnoses":   "Unique Diagnoses",
    "num_procedures":         "Procedure Count",
    "lab_bun_last":           "BUN (Blood Urea Nitrogen)",
    "lab_creatinine_last":    "Creatinine",
    "lab_glucose_last":       "Glucose",
    "lab_hemoglobin_last":    "Hemoglobin",
    "lab_platelet_last":      "Platelet Count",
    "lab_potassium_last":     "Potassium",
    "lab_sodium_last":        "Sodium",
    "lab_wbc_last":           "WBC Count",
    "total_icu_stays":        "ICU Admission Count",
    "total_icu_los":          "ICU Length of Stay (days)",
    "vital_dia_bp_mean":      "Diastolic BP",
    "vital_heart_rate_mean":  "Heart Rate",
    "vital_resp_rate_mean":   "Respiratory Rate",
    "vital_spo2_mean":        "SpO₂",
    "vital_sys_bp_mean":      "Systolic BP",
    "vital_temp_c_mean":      "Body Temperature (°C)",
    "num_unique_drugs":       "Unique Medications",
    "admission_type_encoded": "Admission Type",
    "insurance_encoded":      "Insurance Type",
    "gender_encoded":         "Gender",
    "race_encoded":           "Race/Ethnicity",
}

# Features most relevant per infection type (for SHAP panel ordering)
INFECTION_FEATURES = {
    "vap":    ["vital_resp_rate_mean", "vital_spo2_mean", "vital_temp_c_mean",
               "lab_wbc_last", "total_icu_los", "vital_heart_rate_mean"],
    "clabsi": ["lab_wbc_last", "lab_creatinine_last", "vital_temp_c_mean",
               "total_icu_los", "lab_bun_last", "lab_glucose_last"],
    "cauti":  ["lab_creatinine_last", "lab_bun_last", "vital_temp_c_mean",
               "lab_wbc_last", "total_icu_los", "vital_heart_rate_mean"],
}

ICU_UNITS = ["MICU", "SICU", "CCU", "NSICU", "CVICU"]


# ── Model loading ──────────────────────────────────────────────────────────────

def load_models():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)   # {"lr", "rf", "mlp", "scaler"}


# ── Device heuristics ──────────────────────────────────────────────────────────

def _safe(val, default=0.0):
    return float(val) if pd.notna(val) else default


def derive_device_info(row):
    icu_los   = _safe(row.get("total_icu_los"), 0.0)      # days
    resp_rate = _safe(row.get("vital_resp_rate_mean"), 16)
    spo2      = _safe(row.get("vital_spo2_mean"), 98)

    on_vent  = icu_los > 2.0 and (resp_rate > 20 or spo2 < 96)
    has_cvc  = icu_los > 1.0
    has_cath = icu_los > 0.5

    vent_hours = round(icu_los * 24 * 0.75, 1) if on_vent  else 0.0
    cvc_hours  = round(icu_los * 24,         1) if has_cvc  else 0.0
    cath_hours = round(icu_los * 24,         1) if has_cath else 0.0

    return on_vent, vent_hours, has_cvc, cvc_hours, has_cath, cath_hours


# ── Infection score computation ────────────────────────────────────────────────

def compute_infection_scores(base_risk, on_vent, vent_hours,
                             has_cvc, cvc_hours, has_cath, cath_hours):
    MAX_HRS = 14 * 24   # 14-day cap for device-duration factor
    base = max(0.05, base_risk * 1.2)

    vap    = min(0.95, base * (1.0 + min(vent_hours / MAX_HRS, 1.0) * 2.0)) if on_vent  else max(0.02, base * 0.12)
    clabsi = min(0.95, base * (1.0 + min(cvc_hours  / MAX_HRS, 1.0) * 1.5)) if has_cvc  else max(0.02, base * 0.10)
    cauti  = min(0.95, base * (1.0 + min(cath_hours / MAX_HRS, 1.0) * 1.2)) if has_cath else max(0.02, base * 0.10)

    active = [vap if on_vent else 0, clabsi if has_cvc else 0, cauti if has_cath else 0]
    combined = max(active) if any(active) else base_risk
    combined = min(0.95, max(0.05, combined))

    return round(vap, 2), round(clabsi, 2), round(cauti, 2), round(combined, 2)


# ── SHAP explanations ──────────────────────────────────────────────────────────

def _build_shap_panel(shap_vals_row, feature_values_row, infection_type):
    """
    Build the 6-feature SHAP list for one infection type.
    shap_vals_row   : np.array shape (n_features,)
    feature_values_row : dict {col: raw_value}
    """
    priority_feats = INFECTION_FEATURES[infection_type]

    results = []
    for feat in priority_feats:
        if feat not in FEATURE_COLS:
            continue
        idx  = FEATURE_COLS.index(feat)
        sv   = float(shap_vals_row[idx])
        raw  = feature_values_row.get(feat)

        # -1 is the sentinel for missing values — display as N/A
        is_missing = raw is None or raw == -1.0

        if is_missing:
            val_str = "N/A"
        elif feat in ("vital_temp_c_mean",):
            val_str = f"{raw:.1f}°C"
        elif feat in ("vital_spo2_mean",):
            val_str = f"{raw:.0f}%"
        elif feat in ("vital_heart_rate_mean", "vital_resp_rate_mean",
                      "vital_sys_bp_mean", "vital_dia_bp_mean"):
            val_str = f"{raw:.0f}"
        elif feat in ("total_icu_los",):
            val_str = f"{raw:.1f} days"
        elif feat.startswith("lab_"):
            val_str = f"{raw:.2f}"
        else:
            val_str = str(int(raw))

        results.append({
            "label": FEATURE_LABELS.get(feat, feat),
            "value": val_str,
            "shap":  round(abs(sv), 4),
            "dir":   "up" if sv >= 0 else "down",
        })

    # Sort by |shap| descending, take top 6
    results.sort(key=lambda x: x["shap"], reverse=True)
    return results[:6]


def compute_shap(models, X_row_df):
    """
    Compute SHAP values for one patient row.
    Returns dict {vap: [...], clabsi: [...], cauti: [...]}
    Falls back to RF feature importances if SHAP is unavailable.
    """
    rf = models["rf"]
    feature_values = {col: (None if pd.isna(v) else float(v))
                      for col, v in zip(FEATURE_COLS, X_row_df.values[0])}

    try:
        import shap
        explainer  = shap.TreeExplainer(rf)
        shap_vals  = explainer.shap_values(X_row_df)
        # shap_vals is list[2] for binary; index 1 = positive-class (mortality)
        sv_row = shap_vals[1][0] if isinstance(shap_vals, list) else shap_vals[0]
    except Exception:
        # Fallback: use RF feature importances as proxy SHAP values
        importances = rf.feature_importances_
        # Scale so max = 0.20
        scale = 0.20 / (importances.max() + 1e-9)
        sv_row = importances * scale

    return {
        inf_type: _build_shap_panel(sv_row, feature_values, inf_type)
        for inf_type in ("vap", "clabsi", "cauti")
    }


# ── Main patient builder ───────────────────────────────────────────────────────

def build_patients(models):
    merged = pd.read_csv(MERGED_PATH)
    icu    = merged[merged["total_icu_stays"] > 0].copy().reset_index(drop=True)

    lr     = models["lr"]
    scaler = models["scaler"]

    # Prepare feature matrix for LR model
    X = icu[FEATURE_COLS].fillna(-1).values
    X_scaled = scaler.transform(X)
    base_risks = lr.predict_proba(X_scaled)[:, 1]   # mortality probabilities

    patients = []
    for i, row in icu.iterrows():
        base = float(base_risks[list(icu.index).index(i)])
        on_vent, vent_h, has_cvc, cvc_h, has_cath, cath_h = derive_device_info(row)
        vap, clabsi, cauti, combined = compute_infection_scores(
            base, on_vent, vent_h, has_cvc, cvc_h, has_cath, cath_h
        )

        # Trend: rising if combined > 0.5, stable otherwise
        trend = "rising" if combined >= 0.5 else ("improving" if combined < 0.25 else "stable")

        # Unit assignment via subject_id hash
        unit = ICU_UNITS[int(row["subject_id"]) % len(ICU_UNITS)]

        # Vitals — round to clean display values
        hr   = round(_safe(row.get("vital_heart_rate_mean"), 80))
        temp = round(_safe(row.get("vital_temp_c_mean"),    37.0), 1)
        spo2 = round(_safe(row.get("vital_spo2_mean"),      97))
        rr   = round(_safe(row.get("vital_resp_rate_mean"), 16))
        sbp  = round(_safe(row.get("vital_sys_bp_mean"),   120))
        dbp  = round(_safe(row.get("vital_dia_bp_mean"),    80))

        day_in_icu = max(1, round(_safe(row.get("total_icu_los"), 1)))

        patients.append({
            "id":       f"ICU-{int(row['subject_id'])}",
            "hadm_id":  int(row["hadm_id"]),
            "age":      int(_safe(row.get("age_at_admission"), 50)),
            "gender":   "F" if int(_safe(row.get("gender_encoded"), 0)) == 0 else "M",
            "unit":     unit,
            "dayInICU": day_in_icu,
            "devices": {
                "vent":      on_vent,
                "ventHours": vent_h,
                "cvc":       has_cvc,
                "cvcHours":  cvc_h,
                "cath":      has_cath,
                "cathHours": cath_h,
            },
            "scores": {
                "vap":      vap,
                "clabsi":   clabsi,
                "cauti":    cauti,
                "combined": combined,
            },
            "vitals": {
                "hr":   hr,
                "temp": temp,
                "spo2": spo2,
                "rr":   rr,
                "bp":   f"{sbp}/{dbp}",
            },
            "trend":      trend,
            "base_risk":  round(base, 3),
        })

    return patients


def get_patient_shap(models, patient_id: str):
    """Compute SHAP for a single patient by ID (ICU-{subject_id})."""
    merged = pd.read_csv(MERGED_PATH)
    subject_id = int(patient_id.replace("ICU-", ""))
    row_df = merged[merged["subject_id"] == subject_id]
    if row_df.empty:
        return None
    row_df = row_df.iloc[[0]]
    X = row_df[FEATURE_COLS].fillna(-1)
    return compute_shap(models, X)
