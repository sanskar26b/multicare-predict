# 📋 MIMIC-IV Clinical Database Demo v2.2 — Dataset Guide

> **Source:** [PhysioNet — MIMIC-IV](https://doi.org/10.13026/07hj-2a80)
> **Subjects:** 100 de-identified patients | **Hospital:** Beth Israel Deaconess Medical Center

---

## 📖 Overview

The **MIMIC-IV Clinical Database Demo** is a freely accessible subset of the full MIMIC-IV database. It contains de-identified electronic health records (EHR) for **100 patients** admitted to the Beth Israel Deaconess Medical Center (BIDMC). The demo is useful for workshops, feasibility assessments, and exploratory analysis before requesting full MIMIC-IV access.

> **Note:** Free-text clinical notes are **excluded** from this demo. All dates are shifted into the future for de-identification purposes.

---

## 📁 Directory Structure

```
mimic-iv-clinical-database-demo-2.2/
├── README.md                  # This guide
├── README.txt                 # Original dataset readme
├── LICENSE.txt                # PhysioNet license
├── SHA256SUMS.txt             # File integrity checksums
├── demo_subject_id.csv        # List of 100 subject IDs in the demo
├── prepare_training_data.py   # Script to generate ML-ready data
│
├── training_ready/            # 🤖 Pre-built ML datasets (see section below)
│   ├── training_set.csv       #    Numeric-only, 275 rows × 34 features
│   └── admissions_merged.csv  #    Full merged dataset with text columns
│
├── training_data_source/     # 📦 Raw source files for training pipeline (unzipped)
│   ├── patients.csv           #    Demographics
│   ├── admissions.csv         #    Admission records
│   ├── icustays.csv           #    ICU stay records
│   ├── labevents.csv          #    Laboratory results
│   ├── chartevents.csv        #    ICU vital signs/observations
│   └── ... (10 others)        #    15 total; refer to script for full list
│
├── hosp/                      # 🏥 Hospital-wide data (22 tables)
│   ├── admissions.csv.gz
│   ├── patients.csv.gz
│   ├── transfers.csv.gz
│   ├── services.csv.gz
│   ├── diagnoses_icd.csv.gz
│   ├── procedures_icd.csv.gz
│   ├── labevents.csv.gz
│   ├── microbiologyevents.csv.gz
│   ├── prescriptions.csv.gz
│   ├── pharmacy.csv.gz
│   ├── emar.csv.gz
│   ├── emar_detail.csv.gz
│   ├── poe.csv.gz
│   ├── poe_detail.csv.gz
│   ├── drgcodes.csv.gz
│   ├── hcpcsevents.csv.gz
│   ├── omr.csv.gz
│   ├── provider.csv.gz
│   ├── d_hcpcs.csv.gz          # Dictionary table
│   ├── d_icd_diagnoses.csv.gz  # Dictionary table
│   ├── d_icd_procedures.csv.gz # Dictionary table
│   └── d_labitems.csv.gz       # Dictionary table
│
└── icu/                       # 🩺 ICU-specific data (9 tables)
    ├── icustays.csv.gz
    ├── chartevents.csv.gz
    ├── inputevents.csv.gz
    ├── outputevents.csv.gz
    ├── ingredientevents.csv.gz
    ├── procedureevents.csv.gz
    ├── datetimeevents.csv.gz
    ├── caregiver.csv.gz
    └── d_items.csv.gz          # Dictionary table
```

All data files are **gzip-compressed CSVs** (`.csv.gz`). Read them with:

```python
import pandas as pd
df = pd.read_csv("hosp/admissions.csv.gz", compression="gzip")
```

---

## 🔑 Key Identifiers (Primary & Foreign Keys)

| Identifier | Description | Scope |
|---|---|---|
| `subject_id` | Unique patient identifier | All tables |
| `hadm_id` | Unique hospital admission ID | Per admission |
| `stay_id` | Unique ICU stay ID | ICU tables only |
| `itemid` | Measurement/event type code | Events & dictionary tables |
| `provider_id` | De-identified provider code | Orders & admissions |
| `caregiver_id` | De-identified caregiver code | ICU tables |

### Relationship Hierarchy

```
subject_id (patient)
  └── hadm_id (hospital admission)  — 1 patient has many admissions
        └── stay_id (ICU stay)      — 1 admission can have many ICU stays
```

---

## 🏥 Hospital Module (`hosp/`) — 22 Tables

### Core Patient & Admission Tables

#### `patients.csv.gz` — **100 rows × 6 columns**
Demographics for every patient in the demo.

| Column | Type | Description |
|---|---|---|
| `subject_id` | int | Unique patient ID |
| `gender` | str | `M` or `F` |
| `anchor_age` | int | Patient age at `anchor_year` |
| `anchor_year` | int | Shifted reference year for the patient |
| `anchor_year_group` | str | Real-world year range (e.g., `2011 - 2013`) |
| `dod` | str | Date of death (null for 69 patients = survived) |

#### `admissions.csv.gz` — **275 rows × 16 columns**
One row per hospital admission. 100 unique patients, 275 unique admissions.

| Column | Type | Description | Nulls |
|---|---|---|---|
| `subject_id` | int | Patient ID | 0 |
| `hadm_id` | int | Hospital admission ID | 0 |
| `admittime` | datetime | Admission timestamp | 0 |
| `dischtime` | datetime | Discharge timestamp | 0 |
| `deathtime` | datetime | In-hospital death time | 260 |
| `admission_type` | str | e.g., `URGENT`, `ELECTIVE`, `EMERGENCY` | 0 |
| `admit_provider_id` | str | Admitting provider | 0 |
| `admission_location` | str | Where patient came from | 0 |
| `discharge_location` | str | Where patient went to | 42 |
| `insurance` | str | `Medicare`, `Medicaid`, `Other` | 0 |
| `language` | str | E.g., `ENGLISH` | 0 |
| `marital_status` | str | E.g., `SINGLE`, `MARRIED` | 12 |
| `race` | str | Patient race/ethnicity | 0 |
| `edregtime` | datetime | Emergency dept. registration time | 93 |
| `edouttime` | datetime | Emergency dept. departure time | 93 |
| `hospital_expire_flag` | int | `1` = died during admission, `0` = survived | 0 |

#### `transfers.csv.gz` — **1,190 rows × 7 columns**
Every physical patient location change within the hospital.

| Column | Type | Description |
|---|---|---|
| `subject_id` | int | Patient ID |
| `hadm_id` | float | Hospital admission ID (null for 54 rows) |
| `transfer_id` | int | Unique transfer event ID |
| `eventtype` | str | `admit`, `transfer`, or `discharge` |
| `careunit` | str | Ward/unit name (e.g., `Med/Surg`) — null for 275 rows |
| `intime` | datetime | Entry time to location |
| `outtime` | datetime | Exit time from location — null for 275 rows |

#### `services.csv.gz` — **319 rows × 5 columns**
Records changes in the hospital service caring for the patient.

| Column | Type | Description |
|---|---|---|
| `subject_id` | int | Patient ID |
| `hadm_id` | int | Hospital admission ID |
| `transfertime` | datetime | When the service change occurred |
| `prev_service` | str | Previous service (e.g., `SURG`, `MED`) — null for 275 rows (first service) |
| `curr_service` | str | Current service |

---

### Diagnoses & Procedures

#### `diagnoses_icd.csv.gz` — **4,506 rows × 5 columns**
ICD diagnosis codes assigned to admissions. 1,472 unique codes across 275 admissions.

| Column | Type | Description |
|---|---|---|
| `subject_id` | int | Patient ID |
| `hadm_id` | int | Hospital admission ID |
| `seq_num` | int | Priority ranking of the diagnosis |
| `icd_code` | str | ICD code (versions 9 and 10) |
| `icd_version` | int | `9` (ICD-9) or `10` (ICD-10) |

#### `procedures_icd.csv.gz` — **722 rows × 6 columns**
ICD procedure codes. 352 unique procedure codes across 187 admissions.

| Column | Type | Description |
|---|---|---|
| `subject_id` | int | Patient ID |
| `hadm_id` | int | Hospital admission ID |
| `seq_num` | int | Priority ranking |
| `chartdate` | date | Date of the procedure |
| `icd_code` | str | ICD procedure code |
| `icd_version` | int | `9` or `10` |

#### `drgcodes.csv.gz` — **454 rows × 7 columns**
Diagnosis-Related Group (DRG) codes used for billing/reimbursement.

| Column | Type | Description | Nulls |
|---|---|---|---|
| `subject_id` | int | Patient ID | 0 |
| `hadm_id` | int | Hospital admission ID | 0 |
| `drg_type` | str | DRG system (`HCFA`, `APR`) | 0 |
| `drg_code` | int | DRG code value | 0 |
| `description` | str | DRG description | 0 |
| `drg_severity` | float | Severity index | 233 |
| `drg_mortality` | float | Mortality index | 233 |

#### `hcpcsevents.csv.gz` — **61 rows × 6 columns**
Healthcare Common Procedure Coding System (HCPCS) events.

| Column | Type | Description |
|---|---|---|
| `subject_id` | int | Patient ID |
| `hadm_id` | int | Hospital admission ID |
| `chartdate` | date | Date of the event |
| `hcpcs_cd` | str | HCPCS code |
| `seq_num` | int | Sequence number |
| `short_description` | str | E.g., `Cardiovascular` |

---

### Laboratory & Microbiology

#### `labevents.csv.gz` — **107,727 rows × 16 columns** ⭐ *Largest hospital table*
Lab test results. 498 unique lab items across 100 patients.

| Column | Type | Description | Nulls |
|---|---|---|---|
| `labevent_id` | int | Unique lab event ID | 0 |
| `subject_id` | int | Patient ID | 0 |
| `hadm_id` | float | Hospital admission ID | 28,420 |
| `specimen_id` | int | Specimen identifier | 0 |
| `itemid` | int | Lab test type (→ `d_labitems`) | 0 |
| `order_provider_id` | str | Ordering provider | 90,897 |
| `charttime` | datetime | Time of specimen collection | 0 |
| `storetime` | datetime | Time result was stored | 992 |
| `value` | str | Lab result (text) | 9,588 |
| `valuenum` | float | Lab result (numeric) | 12,481 |
| `valueuom` | str | Unit of measurement | 16,203 |
| `ref_range_lower` | float | Lower reference range | 18,728 |
| `ref_range_upper` | float | Upper reference range | 18,728 |
| `flag` | str | `abnormal` if outside range | 67,452 |
| `priority` | str | `ROUTINE` or `STAT` | 9,329 |
| `comments` | str | Additional notes | 89,273 |

#### `microbiologyevents.csv.gz` — **2,899 rows × 25 columns**
Microbiology culture results including susceptibility testing.

| Column | Type | Description | Nulls |
|---|---|---|---|
| `microevent_id` | int | Unique event ID | 0 |
| `subject_id` | int | Patient ID | 0 |
| `hadm_id` | float | Hospital admission ID | 971 |
| `spec_type_desc` | str | Specimen type (e.g., `SWAB`, `BLOOD CULTURE`) | 0 |
| `test_name` | str | Test performed | 0 |
| `org_name` | str | Organism identified | 1,641 |
| `ab_name` | str | Antibiotic tested | 1,863 |
| `dilution_text` | str | MIC dilution value | 1,900 |
| `interpretation` | str | `S` (sensitive), `R` (resistant), `I` (intermediate) | 1,863 |
| `comments` | str | Additional notes | 811 |

---

### Medications & Pharmacy

#### `prescriptions.csv.gz` — **18,087 rows × 21 columns**
All medication prescriptions.

| Column | Type | Description |
|---|---|---|
| `subject_id` | int | Patient ID |
| `hadm_id` | int | Hospital admission ID |
| `pharmacy_id` | int | Pharmacy order ID |
| `starttime` | datetime | Prescription start |
| `stoptime` | datetime | Prescription end |
| `drug_type` | str | `MAIN`, `BASE`, `ADDITIVE` |
| `drug` | str | Drug name (e.g., `Fentanyl Citrate`) |
| `formulary_drug_cd` | str | Formulary code |
| `ndc` | float | National Drug Code |
| `prod_strength` | str | Product strength |
| `dose_val_rx` | str | Prescribed dose value |
| `dose_unit_rx` | str | Dose unit |
| `route` | str | Administration route (e.g., `IV`, `PO`, `SC`) |

#### `pharmacy.csv.gz` — **15,306 rows × 27 columns**
Detailed pharmacy order records including infusion parameters.

Key columns: `medication`, `status`, `route`, `frequency`, `infusion_type`, `sliding_scale`, `lockout_interval`, `basal_rate`, `duration`

#### `emar.csv.gz` — **35,835 rows × 12 columns**
Electronic Medication Administration Records — when was each medication actually given.

| Column | Type | Description |
|---|---|---|
| `subject_id` | int | Patient ID |
| `hadm_id` | float | Hospital admission ID |
| `emar_id` | str | Unique administration event ID |
| `pharmacy_id` | float | Links to pharmacy order |
| `charttime` | datetime | When the medication was charted |
| `medication` | str | Medication name |
| `event_txt` | str | What happened (e.g., `Applied`, `Read`, `Held`) |

#### `emar_detail.csv.gz` — **72,018 rows × 33 columns**
Detailed administration information including doses, infusion rates, routes, and product descriptions.

---

### Orders

#### `poe.csv.gz` — **45,154 rows × 12 columns**
Provider Order Entry — all clinical orders placed during admissions.

| Column | Type | Description |
|---|---|---|
| `poe_id` | str | Unique order ID |
| `subject_id` | int | Patient ID |
| `hadm_id` | int | Hospital admission ID |
| `ordertime` | datetime | When the order was placed |
| `order_type` | str | e.g., `General Care`, `Medications`, `Lab` |
| `order_subtype` | str | More specific category |
| `transaction_type` | str | `New`, `Change`, `Discontinue` |
| `order_status` | str | `Active`, `Inactive` |

#### `poe_detail.csv.gz` — **3,795 rows × 5 columns**
Additional details for provider orders.

#### `omr.csv.gz` — **2,964 rows × 5 columns**
Outpatient Medical Record data (e.g., vital signs recorded in clinic).

| Column | Type | Description |
|---|---|---|
| `subject_id` | int | Patient ID |
| `chartdate` | date | Date of measurement |
| `result_name` | str | E.g., `Height (Inches)`, `Weight (Lbs)`, `Blood Pressure` |
| `result_value` | str | Recorded value |

---

### Dictionary (Reference) Tables

| Table | Rows | Description |
|---|---|---|
| `d_labitems.csv.gz` | 1,622 | Lab item definitions (`itemid` → `label`, `fluid`, `category`) |
| `d_icd_diagnoses.csv.gz` | 109,775 | ICD diagnosis code → long title (ICD-9 and ICD-10) |
| `d_icd_procedures.csv.gz` | 85,257 | ICD procedure code → long title |
| `d_hcpcs.csv.gz` | 89,200 | HCPCS code → description |
| `provider.csv.gz` | 40,508 | List of de-identified provider IDs (1 column) |

---

## 🩺 ICU Module (`icu/`) — 9 Tables

### `icustays.csv.gz` — **140 rows × 8 columns**
One row per ICU stay. 100 patients, 128 admissions, 140 ICU stays.

| Column | Type | Description |
|---|---|---|
| `subject_id` | int | Patient ID |
| `hadm_id` | int | Hospital admission ID |
| `stay_id` | int | Unique ICU stay ID |
| `first_careunit` | str | First ICU unit (e.g., `Medical Intensive Care Unit (MICU)`) |
| `last_careunit` | str | Last ICU unit (may differ from first if transferred) |
| `intime` | datetime | ICU admission time |
| `outtime` | datetime | ICU discharge time |
| `los` | float | Length of stay in **days** (fractional) |

### `chartevents.csv.gz` — **668,862 rows × 11 columns** ⭐ *Largest table in the entire dataset*
All charted clinical observations (vitals, assessments, scores, etc.). 1,318 unique item types.

| Column | Type | Description | Nulls |
|---|---|---|---|
| `subject_id` | int | Patient ID | 0 |
| `hadm_id` | int | Hospital admission ID | 0 |
| `stay_id` | int | ICU stay ID | 0 |
| `caregiver_id` | float | Who charted | 24,240 |
| `charttime` | datetime | Time of observation | 0 |
| `storetime` | datetime | Time it was recorded | 1,159 |
| `itemid` | int | What was measured (→ `d_items`) | 0 |
| `value` | str | Observation value (text) | 20,730 |
| `valuenum` | float | Observation value (numeric) | 411,388 |
| `valueuom` | str | Unit of measurement | 506,291 |
| `warning` | float | Alert flag | 1,159 |

### `inputevents.csv.gz` — **20,404 rows × 26 columns**
All fluids and medications administered via IV, bolus, etc.

| Key Column | Description |
|---|---|
| `itemid` | Fluid/drug type (→ `d_items`) |
| `amount` / `amountuom` | Volume administered and unit |
| `rate` / `rateuom` | Infusion rate and unit |
| `ordercategoryname` | E.g., `08-Antibiotics (IV)`, `02-Fluids (Crystalloids)` |
| `patientweight` | Patient weight in kg at time of input |
| `statusdescription` | E.g., `FinishedRunning`, `Paused`, `Stopped` |

### `outputevents.csv.gz` — **9,362 rows × 9 columns**
All fluid output measurements (urine, drainage, etc.).

| Column | Type | Description |
|---|---|---|
| `stay_id` | int | ICU stay ID |
| `itemid` | int | Output type (→ `d_items`) |
| `charttime` | datetime | Time of measurement |
| `value` | int | Output volume |
| `valueuom` | str | Always `ml` |

### `ingredientevents.csv.gz` — **25,728 rows × 17 columns**
Breakdown of individual ingredients within IV solutions.

### `procedureevents.csv.gz` — **1,468 rows × 22 columns**
ICU procedures such as line insertions, intubation, ventilation.

| Key Column | Description |
|---|---|
| `itemid` | Procedure type (82 unique) |
| `value` / `valueuom` | Duration in minutes |
| `location` / `locationcategory` | Where the procedure was performed (e.g., `Right Antecubital`, `Peripheral`) |
| `ordercategoryname` | E.g., `Ventilation`, `Invasive Lines`, `Peripheral Lines` |

### `datetimeevents.csv.gz` — **15,280 rows × 10 columns**
Date/time-type charted events (e.g., consent dates, procedure dates).

### `caregiver.csv.gz` — **15,468 rows × 1 column**
List of unique de-identified caregiver IDs.

### `d_items.csv.gz` — **4,014 rows × 9 columns** *(Dictionary)*
Definitions for all ICU `itemid` values.

| Column | Description |
|---|---|
| `itemid` | Unique item identifier |
| `label` | Human-readable name (e.g., `Heart Rate`, `Gender`) |
| `abbreviation` | Short name |
| `linksto` | Which table uses this item (`chartevents`, `inputevents`, etc.) |
| `category` | Category (e.g., `Respiratory`, `Hemodynamics`, `ADT`) |
| `unitname` | Default unit (e.g., `bpm`, `%`, `mmHg`) |
| `param_type` | `Numeric`, `Text`, `Date`, etc. |
| `lownormalvalue` / `highnormalvalue` | Normal reference range |

---

## 📊 Dataset Summary at a Glance

| Metric | Value |
|---|---|
| **Total patients** | 100 |
| **Hospital admissions** | 275 |
| **ICU stays** | 140 |
| **Unique lab tests** | 498 |
| **Unique ICU chart items** | 1,318 |
| **Total lab results** | 107,727 |
| **Total ICU chart events** | 668,862 |
| **Total medication prescriptions** | 18,087 |
| **Total med administrations (eMAR)** | 35,835 |
| **Total provider orders** | 45,154 |
| **Unique ICD diagnosis codes used** | 1,472 |
| **Unique ICD procedure codes used** | 352 |
| **Unique providers** | 40,508 |
| **Unique caregivers** | 15,468 |

---

## 🔗 Table Relationships (Entity-Relationship Map)

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│  patients    │──1:N─│  admissions   │──1:N─│  icustays     │
│  (100)       │      │  (275)        │      │  (140)        │
└─────────────┘      └──────┬───────┘      └──────┬───────┘
                            │                      │
          ┌─────────────────┼──────────────────────┤
          │                 │                      │
    ┌─────┴─────┐    ┌──────┴──────┐        ┌──────┴──────┐
    │diagnoses_ │    │ labevents   │        │ chartevents │
    │icd (4506) │    │ (107,727)   │        │ (668,862)   │
    └───────────┘    └─────────────┘        └─────────────┘
    ┌───────────┐    ┌─────────────┐        ┌─────────────┐
    │procedures_│    │ microbiology│        │ inputevents │
    │icd (722)  │    │ (2,899)     │        │ (20,404)    │
    └───────────┘    └─────────────┘        └─────────────┘
    ┌───────────┐    ┌─────────────┐        ┌─────────────┐
    │ drgcodes  │    │prescriptions│        │ outputevents│
    │ (454)     │    │ (18,087)    │        │ (9,362)     │
    └───────────┘    └─────────────┘        └─────────────┘
    ┌───────────┐    ┌─────────────┐        ┌─────────────┐
    │ services  │    │ emar        │        │ procedure   │
    │ (319)     │    │ (35,835)    │        │ events(1468)│
    └───────────┘    └─────────────┘        └─────────────┘
    ┌───────────┐    ┌─────────────┐        ┌─────────────┐
    │ transfers │    │ pharmacy    │        │ ingredient  │
    │ (1,190)   │    │ (15,306)    │        │ events      │
    └───────────┘    └─────────────┘        │ (25,728)    │
    ┌───────────┐    ┌─────────────┐        └─────────────┘
    │hcpcsevents│    │ poe         │        ┌─────────────┐
    │ (61)      │    │ (45,154)    │        │ datetime    │
    └───────────┘    └─────────────┘        │ events      │
                     ┌─────────────┐        │ (15,280)    │
                     │ omr         │        └─────────────┘
                     │ (2,964)     │
                     └─────────────┘

    DICTIONARY TABLES (lookup references):
    ├── d_labitems      (1,622 items)     → labevents.itemid
    ├── d_items         (4,014 items)     → chartevents/input/output/procedure/datetime/ingredient
    ├── d_icd_diagnoses (109,775 codes)   → diagnoses_icd.icd_code
    ├── d_icd_procedures(85,257 codes)    → procedures_icd.icd_code
    └── d_hcpcs         (89,200 codes)    → hcpcsevents.hcpcs_cd
```

---

## 🧪 Common Use Cases & Example Queries

### 1. Get patient demographics with admission info

```python
import pandas as pd

patients = pd.read_csv("hosp/patients.csv.gz")
admissions = pd.read_csv("hosp/admissions.csv.gz")

df = admissions.merge(patients, on="subject_id")
print(df[["subject_id", "hadm_id", "gender", "anchor_age", "admission_type", "insurance"]].head())
```

### 2. Look up diagnoses with human-readable descriptions

```python
diagnoses = pd.read_csv("hosp/diagnoses_icd.csv.gz")
d_icd = pd.read_csv("hosp/d_icd_diagnoses.csv.gz")

df = diagnoses.merge(d_icd, on=["icd_code", "icd_version"])
print(df[["subject_id", "hadm_id", "icd_code", "long_title"]].head(10))
```

### 3. Get all lab results for a specific test (e.g., Lactate)

```python
labitems = pd.read_csv("hosp/d_labitems.csv.gz")
lactate_id = labitems[labitems["label"] == "Lactate"]["itemid"].values[0]

labs = pd.read_csv("hosp/labevents.csv.gz")
lactate = labs[labs["itemid"] == lactate_id]
print(f"Lactate results: {len(lactate)} records")
print(lactate[["subject_id", "charttime", "valuenum", "valueuom", "flag"]].head())
```

### 4. Analyze ICU length of stay

```python
icu = pd.read_csv("icu/icustays.csv.gz")
print(f"Median ICU LOS: {icu['los'].median():.2f} days")
print(f"Mean ICU LOS:   {icu['los'].mean():.2f} days")
print(f"Max ICU LOS:    {icu['los'].max():.2f} days")
```

### 5. Get ICU vital signs (Heart Rate, Blood Pressure, etc.)

```python
d_items = pd.read_csv("icu/d_items.csv.gz")
hr_id = d_items[d_items["label"] == "Heart Rate"]["itemid"].values[0]

chart = pd.read_csv("icu/chartevents.csv.gz")
hr = chart[chart["itemid"] == hr_id]
print(hr[["subject_id", "stay_id", "charttime", "valuenum"]].head())
```

### 6. Medication administration timeline

```python
emar = pd.read_csv("hosp/emar.csv.gz")
emar["charttime"] = pd.to_datetime(emar["charttime"])

# Top 10 most administered medications
print(emar["medication"].value_counts().head(10))
```

---

## 🤖 Training-Ready ML Dataset (`training_ready/`)

A pre-built, ML-ready dataset is provided in the `training_ready/` folder. It was generated by the `prepare_training_data.py` script, which merges 11 core tables (patients, admissions, diagnoses, procedures, labs, prescriptions, ICU stays, chart events, and dictionary tables) into a single flat dataset at the **admission level** (one row per hospital admission).

### Output Files

```
training_ready/
├── training_set.csv         — Numeric-only, ML-ready (275 rows × 34 features)
└── admissions_merged.csv    — Full merged dataset with human-readable text columns
```

### Source Files Used for Training

The `training_data_source/` folder contains the specific raw tables extracted from `hosp/` and `icu/` that are used by the `prepare_training_data.py` script. These represent the "high-value" clinical tables for most ML tasks:
- **Demographics & Stays**: `patients.csv`, `admissions.csv`, `icustays.csv`
- **Clinical Events**: `labevents.csv`, `chartevents.csv`, `prescriptions.csv`, `inputevents.csv`, `outputevents.csv`
- **Diagnoses & Logic**: `diagnoses_icd.csv`, `procedures_icd.csv`, `procedureevents.csv`
- **Dictionaries**: `d_labitems.csv`, `d_items.csv`, `d_icd_diagnoses.csv`, `d_icd_procedures.csv`

### Target Variable

| Variable | Column | Type | Description |
|---|---|---|---|
| **Mortality** | `mortality` | Binary (0/1) | In-hospital death. `1` = died, `0` = survived |

**Class distribution:** ~5.5% positive (15 deaths out of 275 admissions) — this is an **imbalanced** classification problem.

### Feature Reference (34 columns in `training_set.csv`)

#### Admission & Demographics

| Feature | Type | Description |
|---|---|---|
| `hospital_expire_flag` | int | Same as `mortality` (raw source column) |
| `anchor_age` | int | Patient age at anchor year |
| `age_at_admission` | int | Estimated age at time of admission |
| `gender_encoded` | int | 0 = F, 1 = M |
| `race_encoded` | int | Encoded race/ethnicity category |
| `admission_type_encoded` | int | Encoded admission type (URGENT, ELECTIVE, etc.) |
| `insurance_encoded` | int | Encoded insurance type (Medicare, Medicaid, Other) |

#### Timing & Length of Stay

| Feature | Type | Description |
|---|---|---|
| `los_hours` | float | Hospital length of stay in hours |
| `los_days` | float | Hospital length of stay in days |
| `ed_wait_hours` | float | Time spent in the Emergency Department (hours) |
| `admit_hour` | int | Hour of day of admission (0–23) |
| `admit_dayofweek` | int | Day of week of admission (0=Mon, 6=Sun) |
| `is_weekend_admit` | int | 1 if admitted on Saturday or Sunday |

#### Diagnoses & Procedures

| Feature | Type | Description |
|---|---|---|
| `num_diagnoses` | int | Total ICD diagnosis codes for the admission |
| `num_unique_diagnoses` | int | Unique ICD codes for the admission |
| `num_procedures` | int | Number of ICD-coded procedures performed |

#### Lab Results (last recorded value per admission)

| Feature | Type | Description |
|---|---|---|
| `lab_bun_last` | float | Blood Urea Nitrogen (mg/dL) |
| `lab_creatinine_last` | float | Creatinine (mg/dL) — kidney function |
| `lab_glucose_last` | float | Glucose (mg/dL) |
| `lab_hemoglobin_last` | float | Hemoglobin (g/dL) — oxygen carrying capacity |
| `lab_platelet_last` | float | Platelet count (K/uL) — clotting |
| `lab_potassium_last` | float | Potassium (mEq/L) — electrolyte |
| `lab_sodium_last` | float | Sodium (mEq/L) — electrolyte |
| `lab_wbc_last` | float | White Blood Cell count (K/uL) — infection/immune |

#### ICU Stay

| Feature | Type | Description |
|---|---|---|
| `total_icu_stays` | int | Number of ICU stays during admission (0 = no ICU) |
| `total_icu_los` | float | Total ICU length of stay in days |

#### ICU Vital Signs (mean values across all charted observations)

| Feature | Type | Description |
|---|---|---|
| `vital_heart_rate_mean` | float | Mean heart rate (bpm) |
| `vital_sys_bp_mean` | float | Mean systolic blood pressure (mmHg) |
| `vital_dia_bp_mean` | float | Mean diastolic blood pressure (mmHg) |
| `vital_resp_rate_mean` | float | Mean respiratory rate (breaths/min) |
| `vital_spo2_mean` | float | Mean SpO2 — oxygen saturation (%) |
| `vital_temp_c_mean` | float | Mean body temperature (°C) |

#### Medications

| Feature | Type | Description |
|---|---|---|
| `num_unique_drugs` | int | Number of distinct drugs prescribed |

> **Missing values** are filled with `-1` as a sentinel value. This is suitable for tree-based models (XGBoost, Random Forest). For linear models or neural networks, consider imputing with mean/median instead.

### Quick Start — Train a Model

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Load training-ready data
df = pd.read_csv("training_ready/training_set.csv")

# Separate features and target
X = df.drop(columns=["mortality", "hospital_expire_flag"])
y = df["mortality"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train a model
clf = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
clf.fit(X_train, y_train)

# Evaluate
print(classification_report(y_test, clf.predict(X_test)))
```

### Re-generating the Training Data

To re-run the preparation pipeline (e.g., after modifying feature engineering):

```bash
python prepare_training_data.py
```

The script reads directly from `.csv.gz` files — no manual decompression required.

---

## ⚠️ Important Notes

1. **Date Shifting:** All dates are shifted into the future (years like 2100–2200) to protect patient privacy. Relative time differences (e.g., length of stay) remain accurate.

2. **ICD Versions:** The dataset contains both ICD-9 and ICD-10 codes. Always filter or join on **both** `icd_code` AND `icd_version`.

3. **Nullable Foreign Keys:** Some `hadm_id` values are null in `labevents` (28,420 rows) and `microbiologyevents` (971 rows) — these represent outpatient tests.

4. **Large Tables:** `chartevents` has 668,862 rows. Consider filtering by `itemid` or `stay_id` before loading to conserve memory.

5. **De-identified Text:** Some text fields contain `___` placeholders where personally identifiable information was redacted.

6. **Dictionary Tables Are Comprehensive:** The `d_icd_*` and `d_hcpcs` tables contain the full code dictionaries, not just codes used in this demo subset.

---

## 📚 Citation

If you use this dataset, please cite:

> Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023). MIMIC-IV Clinical Database Demo (version 2.2). PhysioNet. https://doi.org/10.13026/dp1f-ex47

---

## 📄 License

This dataset is released under the [PhysioNet Credentialed Health Data License 1.5.0](https://physionet.org/content/mimiciv-demo/view-license/2.2/).
