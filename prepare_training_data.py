"""
MIMIC-IV Demo — Training-Ready Data Preparation (Memory Efficient)
===================================================================
This script:
  1. Loads key tables directly from .csv.gz files (no disk decompression needed)
  2. Merges key tables into a unified, ML-ready dataset
  3. Engineers features from admissions, diagnoses, labs, ICU stays, vitals, meds
  4. Handles missing values, encodes categoricals, and outputs clean CSVs
"""

import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE, "training_ready")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# STEP 1: Define Table Loading Function
# ──────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Loading core tables from training_data_source/")
print("=" * 60)

DATA_SOURCE = os.path.join(BASE, "training_data_source")


def load_csv(name):
    path = os.path.join(DATA_SOURCE, f"{name}.csv")
    if not os.path.exists(path):
        print(f"  ⚠ {name}: File not found at {path}")
        return None
    df = pd.read_csv(path, low_memory=False)
    print(f"  ✓ {name}: {len(df):,} rows × {len(df.columns)} cols")
    return df


patients = load_csv("patients")
admissions = load_csv("admissions")
diagnoses = load_csv("diagnoses_icd")
procedures = load_csv("procedures_icd")
labevents = load_csv("labevents")
prescriptions = load_csv("prescriptions")
d_labitems = load_csv("d_labitems")
d_icd_diag = load_csv("d_icd_diagnoses")
icustays = load_csv("icustays")
chartevents = load_csv("chartevents")
d_items = load_csv("d_items")

print()

# ──────────────────────────────────────────────
# STEP 2: Build admission-level training dataset
# ──────────────────────────────────────────────
print("=" * 60)
print("STEP 2: Building admission-level features")
print("=" * 60)

# --- 2a. Base: patients + admissions ---
for col in ["admittime", "dischtime", "deathtime", "edregtime", "edouttime"]:
    admissions[col] = pd.to_datetime(admissions[col])

df = admissions.merge(patients, on="subject_id", how="left")

# Basic features
df["los_hours"] = (df["dischtime"] - df["admittime"]).dt.total_seconds() / 3600
df["los_days"] = df["los_hours"] / 24
df["ed_wait_hours"] = (df["edouttime"] - df["edregtime"]).dt.total_seconds() / 3600
df["age_at_admission"] = df["anchor_age"] + (
    df["admittime"].dt.year - df["anchor_year"]
)
df["mortality"] = df["hospital_expire_flag"]
df["admit_hour"] = df["admittime"].dt.hour
df["admit_dayofweek"] = df["admittime"].dt.dayofweek
df["is_weekend_admit"] = (df["admit_dayofweek"] >= 5).astype(int)

print(f"  ✓ Base table: {len(df)} admissions")

# --- 2b. Diagnosis features ---
print("  → Engineering diagnosis features...")
diag_counts = (
    diagnoses.groupby("hadm_id")
    .agg(
        num_diagnoses=("icd_code", "count"),
        num_unique_diagnoses=("icd_code", "nunique"),
    )
    .reset_index()
)
df = df.merge(diag_counts, on="hadm_id", how="left")

# Get primary diagnosis (seq_num = 1)
primary_diag = diagnoses[diagnoses["seq_num"] == 1][
    ["hadm_id", "icd_code", "icd_version"]
]
primary_diag = primary_diag.merge(
    d_icd_diag, on=["icd_code", "icd_version"], how="left"
)
primary_diag.rename(
    columns={"long_title": "primary_diag_title", "icd_code": "prim_icd_code"},
    inplace=True,
)
df = df.merge(
    primary_diag[["hadm_id", "prim_icd_code", "primary_diag_title"]],
    on="hadm_id",
    how="left",
)

# --- 2c. Procedure features ---
print("  → Engineering procedure features...")
proc_counts = (
    procedures.groupby("hadm_id")
    .agg(num_procedures=("icd_code", "count"))
    .reset_index()
)
df = df.merge(proc_counts, on="hadm_id", how="left")
df["num_procedures"] = df["num_procedures"].fillna(0).astype(int)

# --- 2d. Lab features ---
print("  → Processing lab items (pivot)...")
# Important lab items (itemids found in d_labitems)
# Glucose: 50931, Creatinine: 50912, Hemoglobin: 51222, WBC: 51301, Potassium: 50971, Sodium: 50983, Platelets: 51265, BUN: 51006
key_lab_map = {
    50931: "glucose",
    50912: "creatinine",
    51222: "hemoglobin",
    51301: "wbc",
    50971: "potassium",
    50983: "sodium",
    51265: "platelet",
    51006: "bun",
}

lab_subset = labevents[labevents["itemid"].isin(key_lab_map.keys())].dropna(
    subset=["hadm_id"]
)
lab_subset["hadm_id"] = lab_subset["hadm_id"].astype(int)
lab_subset["lab_name"] = lab_subset["itemid"].map(key_lab_map)

# Take the last recorded value for each lab per admission
lab_last = (
    lab_subset.sort_values(["hadm_id", "charttime"])
    .groupby(["hadm_id", "lab_name"])["valuenum"]
    .last()
    .unstack()
)
lab_last.columns = [f"lab_{c}_last" for c in lab_last.columns]
df = df.merge(lab_last, on="hadm_id", how="left")

# --- 2e. ICU and Vital signs ---
print("  → Engineering ICU and vital sign features...")
# ICU summary
icu_agg = (
    icustays.groupby("hadm_id")
    .agg(total_icu_stays=("stay_id", "count"), total_icu_los=("los", "sum"))
    .reset_index()
)
df = df.merge(icu_agg, on="hadm_id", how="left")
df["total_icu_stays"] = df["total_icu_stays"].fillna(0).astype(int)

# Vital sign itemids (itemids from d_items)
# Heart rate: 220045, Systolic BP: 220050, Diastolic BP: 220051, Resp rate: 220210, SpO2: 220277, Temp C: 223762
vital_map = {
    220045: "heart_rate",
    220050: "sys_bp",
    220051: "dia_bp",
    220210: "resp_rate",
    220277: "spo2",
    223762: "temp_c",
}

vitals = chartevents[chartevents["itemid"].isin(vital_map.keys())].copy()
vitals["vital_name"] = vitals["itemid"].map(vital_map)
# Take mean of vitals per admission for simplicity
vitals_mean = vitals.groupby(["hadm_id", "vital_name"])["valuenum"].mean().unstack()
vitals_mean.columns = [f"vital_{c}_mean" for c in vitals_mean.columns]
df = df.merge(vitals_mean, on="hadm_id", how="left")

# --- 2f. Medication features ---
print("  → Engineering medication features...")
med_stats = (
    prescriptions.groupby("hadm_id")
    .agg(num_unique_drugs=("drug", "nunique"))
    .reset_index()
)
df = df.merge(med_stats, on="hadm_id", how="left")
df["num_unique_drugs"] = df["num_unique_drugs"].fillna(0).astype(int)

print()

# ──────────────────────────────────────────────
# STEP 3: Encoding Categorical Variables
# ──────────────────────────────────────────────
print("=" * 60)
print("STEP 3: Encoding and cleanup")
print("=" * 60)

cat_cols = ["admission_type", "insurance", "gender", "race"]
for col in cat_cols:
    df[col] = df[col].fillna("Unknown")
    df[f"{col}_encoded"] = df[col].astype("category").cat.codes
    print(f"  ✓ {col}: {df[col].nunique()} categories")

# Final ML-ready version
drop_cols = [
    "subject_id",
    "hadm_id",
    "admittime",
    "dischtime",
    "deathtime",
    "admit_provider_id",
    "admission_location",
    "discharge_location",
    "language",
    "marital_status",
    "edregtime",
    "edouttime",
    "dod",
    "anchor_year_group",
    "anchor_year",
    "primary_diag_title",
    "prim_icd_code",
] + cat_cols

df_ml = df.drop(columns=drop_cols, errors="ignore")

# Fill missing numerical with -1
numerical_cols = df_ml.select_dtypes(include=[np.number]).columns
df_ml[numerical_cols] = df_ml[numerical_cols].fillna(-1)

print()

# ──────────────────────────────────────────────
# STEP 4: Save Training-Ready Data
# ──────────────────────────────────────────────
print("=" * 60)
print("STEP 4: Saving files to 'training_ready/'")
print("=" * 60)

full_path = os.path.join(OUTPUT_DIR, "admissions_merged.csv")
ml_path = os.path.join(OUTPUT_DIR, "training_set.csv")

df.to_csv(full_path, index=False)
df_ml.to_csv(ml_path, index=False)

print(f"  ✓ Merged (full): {full_path}")
print(f"  ✓ ML Ready:      {ml_path}")
print(f"    - Training-ready rows: {len(df_ml)}")
print(f"    - Features: {len(df_ml.columns)}")

print("\n🚀 DONE! Dataset is training-ready.")
