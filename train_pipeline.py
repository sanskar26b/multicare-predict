"""
EDIPS — ICU Mortality Prediction Training Pipeline
====================================================
This script trains three models on the MIMIC-IV training-ready dataset:
  1. Logistic Regression  (baseline)
  2. Random Forest         (primary ML model)
  3. MLP Neural Network    (deep learning model)

Evaluation metrics: AUROC, AUPRC, F1-score
Outputs: best_model.pt, metrics.json, training_plot.png,
         feature_importance.png, evaluation_results.txt

Author : EDIPS Team
Dataset: MIMIC-IV Clinical Database Demo v2.2 (100 patients, 275 admissions)
Target : In-hospital mortality (binary 0/1)
"""

import os
import json
import pickle
import warnings
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend (no GUI needed)
import matplotlib.pyplot as plt

# -- Scikit-learn imports --
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    f1_score,
    accuracy_score,
    classification_report,
    confusion_matrix,
)

warnings.filterwarnings("ignore")

# ============================================================
# 0. CONFIGURATION
# ============================================================
# All paths are relative to this script's location so the
# project stays self-contained and portable.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "training_ready", "training_set.csv")
RANDOM_STATE = 42  # For reproducibility
TEST_SIZE = 0.15  # 15% for test
VAL_SIZE = 0.15  # 15% for validation (from remaining 85%)

# Columns to drop (target & its duplicate)
TARGET_COL = "mortality"
DROP_COLS = ["hospital_expire_flag"]  # Same info as mortality

print("=" * 60)
print("EDIPS — ICU Mortality Prediction Training Pipeline")
print("=" * 60)

# ============================================================
# 1. LOAD AND INSPECT DATA
# ============================================================
print("\n📂 STEP 1: Loading dataset...")

df = pd.read_csv(DATA_PATH)
print(f"   Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"   File: {DATA_PATH}")

# Separate features (X) and target (y)
y = df[TARGET_COL].values
X = df.drop(columns=[TARGET_COL] + DROP_COLS, errors="ignore")
feature_names = list(X.columns)

print(f"\n   Target: '{TARGET_COL}'")
print(f"   Class distribution:")
print(f"     - Survived (0): {(y == 0).sum()} ({(y == 0).mean()*100:.1f}%)")
print(f"     - Died     (1): {(y == 1).sum()} ({(y == 1).mean()*100:.1f}%)")
print(f"   Features: {len(feature_names)}")
print(f"   Feature list: {feature_names}")

# ============================================================
# 2. TRAIN / VALIDATION / TEST SPLIT
# ============================================================
print("\n📊 STEP 2: Splitting data (70% train / 15% val / 15% test)...")

# First split: separate test set (15%)
X_temp, X_test, y_temp, y_test = train_test_split(
    X.values, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)

# Second split: separate validation from training
# 15% of original ≈ 17.6% of remaining 85%
val_fraction = VAL_SIZE / (1 - TEST_SIZE)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=val_fraction, random_state=RANDOM_STATE, stratify=y_temp
)

print(f"   Train: {X_train.shape[0]} samples")
print(f"   Val:   {X_val.shape[0]} samples")
print(f"   Test:  {X_test.shape[0]} samples")

# ============================================================
# 3. FEATURE SCALING
# ============================================================
print("\n⚙️  STEP 3: Scaling features (StandardScaler)...")

# StandardScaler: fit on training data only, transform all splits
# This prevents data leakage from test/val into training
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

# Replace any remaining NaN values with 0 after scaling
X_train_scaled = np.nan_to_num(X_train_scaled, nan=0.0)
X_val_scaled = np.nan_to_num(X_val_scaled, nan=0.0)
X_test_scaled = np.nan_to_num(X_test_scaled, nan=0.0)

print("   ✓ Scaler fitted on training data and applied to all splits.")

# ============================================================
# 4. MODEL 1 — LOGISTIC REGRESSION (Baseline)
# ============================================================
print("\n" + "=" * 60)
print("🔬 MODEL 1: Logistic Regression (Baseline)")
print("=" * 60)

lr_model = LogisticRegression(
    class_weight="balanced",  # Automatically adjust weights for imbalanced classes
    max_iter=1000,  # Ensure convergence
    random_state=RANDOM_STATE,
    solver="lbfgs",  # Good default solver for small datasets
)
lr_model.fit(X_train_scaled, y_train)

# Predict probabilities and class labels on test set
lr_probs = lr_model.predict_proba(X_test_scaled)[:, 1]
lr_preds = lr_model.predict(X_test_scaled)

# Calculate metrics
lr_auroc = roc_auc_score(y_test, lr_probs)
lr_auprc = average_precision_score(y_test, lr_probs)
lr_f1 = f1_score(y_test, lr_preds, zero_division=0)
lr_acc = accuracy_score(y_test, lr_preds)

print(f"   AUROC:     {lr_auroc:.4f}")
print(f"   AUPRC:     {lr_auprc:.4f}")
print(f"   F1:        {lr_f1:.4f}")
print(f"   Accuracy:  {lr_acc:.4f}")
print(f"\n   Classification Report:")
print(
    classification_report(
        y_test, lr_preds, target_names=["Survived", "Died"], zero_division=0
    )
)

# ============================================================
# 5. MODEL 2 — RANDOM FOREST
# ============================================================
print("=" * 60)
print("🌲 MODEL 2: Random Forest")
print("=" * 60)

rf_model = RandomForestClassifier(
    n_estimators=100,  # 100 decision trees in the ensemble
    class_weight="balanced",  # Handle class imbalance
    max_depth=10,  # Prevent overfitting on small data
    min_samples_leaf=5,  # Regularization: each leaf has at least 5 samples
    random_state=RANDOM_STATE,
)
# Random Forest works fine on unscaled data (tree-based model)
rf_model.fit(X_train, y_train)

# Predict on test set
rf_probs = rf_model.predict_proba(X_test)[:, 1]
rf_preds = rf_model.predict(X_test)

# Calculate metrics
rf_auroc = roc_auc_score(y_test, rf_probs)
rf_auprc = average_precision_score(y_test, rf_probs)
rf_f1 = f1_score(y_test, rf_preds, zero_division=0)
rf_acc = accuracy_score(y_test, rf_preds)

print(f"   AUROC:     {rf_auroc:.4f}")
print(f"   AUPRC:     {rf_auprc:.4f}")
print(f"   F1:        {rf_f1:.4f}")
print(f"   Accuracy:  {rf_acc:.4f}")
print(f"\n   Classification Report:")
print(
    classification_report(
        y_test, rf_preds, target_names=["Survived", "Died"], zero_division=0
    )
)

# -- Feature Importance Plot --
# Random Forest gives us feature importances based on Gini impurity reduction
importances = rf_model.feature_importances_
sorted_idx = np.argsort(importances)[-15:]  # Top 15 most important features

fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(
    [feature_names[i] for i in sorted_idx],
    importances[sorted_idx],
    color="#2196F3",
    edgecolor="#1565C0",
)
ax.set_xlabel("Feature Importance (Gini)", fontsize=12)
ax.set_title(
    "Random Forest — Top 15 Feature Importances", fontsize=14, fontweight="bold"
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
fi_path = os.path.join(BASE_DIR, "feature_importance.png")
plt.savefig(fi_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"\n   📊 Feature importance plot saved → {fi_path}")

# ============================================================
# 6. MODEL 3 — MLP NEURAL NETWORK (sklearn)
# ============================================================
print("\n" + "=" * 60)
print("🧠 MODEL 3: MLP Neural Network")
print("=" * 60)

# MLPClassifier: a multi-layer perceptron for classification
# Architecture: Input → 64 neurons → 32 neurons → Output
mlp_model = MLPClassifier(
    hidden_layer_sizes=(64, 32),  # Two hidden layers
    activation="relu",  # ReLU activation function
    solver="adam",  # Adam optimizer (adaptive learning rate)
    alpha=1e-4,  # L2 regularization to prevent overfitting
    batch_size=32,  # Mini-batch size
    learning_rate="adaptive",  # Reduce LR when loss plateaus
    learning_rate_init=1e-3,  # Initial learning rate
    max_iter=300,  # Maximum training epochs
    early_stopping=True,  # Stop if validation score stops improving
    validation_fraction=0.2,  # Use 20% of training data for internal validation
    n_iter_no_change=20,  # Patience: stop after 20 epochs with no improvement
    random_state=RANDOM_STATE,
    verbose=False,
)

# Train the MLP on scaled features
mlp_model.fit(X_train_scaled, y_train)

# Track training loss curves (sklearn stores them during training)
train_losses = mlp_model.loss_curve_
val_scores = mlp_model.validation_scores_ if hasattr(mlp_model, "validation_scores_") else []

print(f"   Training completed in {mlp_model.n_iter_} epochs")
print(f"   Architecture: Input({X_train_scaled.shape[1]}) → 64 → 32 → Output(2)")

# Predict on test set
mlp_probs = mlp_model.predict_proba(X_test_scaled)[:, 1]
mlp_preds = mlp_model.predict(X_test_scaled)

# Calculate metrics
mlp_auroc = roc_auc_score(y_test, mlp_probs)
mlp_auprc = average_precision_score(y_test, mlp_probs)
mlp_f1 = f1_score(y_test, mlp_preds, zero_division=0)
mlp_acc = accuracy_score(y_test, mlp_preds)

print(f"\n   Test Results:")
print(f"   AUROC:     {mlp_auroc:.4f}")
print(f"   AUPRC:     {mlp_auprc:.4f}")
print(f"   F1:        {mlp_f1:.4f}")
print(f"   Accuracy:  {mlp_acc:.4f}")
print(f"\n   Classification Report:")
print(
    classification_report(
        y_test, mlp_preds, target_names=["Survived", "Died"], zero_division=0
    )
)

# --- Training loss curve plot ---
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot training loss
color_train = "#FF5722"
ax1.plot(train_losses, label="Train Loss", color=color_train, linewidth=2)
ax1.set_xlabel("Epoch", fontsize=12)
ax1.set_ylabel("Loss", fontsize=12, color=color_train)
ax1.tick_params(axis="y", labelcolor=color_train)

# Plot validation accuracy on a second y-axis if available
if val_scores:
    ax2 = ax1.twinx()
    color_val = "#2196F3"
    ax2.plot(val_scores, label="Val Accuracy", color=color_val, linewidth=2, linestyle="--")
    ax2.set_ylabel("Validation Accuracy", fontsize=12, color=color_val)
    ax2.tick_params(axis="y", labelcolor=color_val)
    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=11, loc="center right")
else:
    ax1.legend(fontsize=11)

ax1.set_title("MLP Training — Loss & Validation Curves", fontsize=14, fontweight="bold")
ax1.spines["top"].set_visible(False)
ax1.grid(alpha=0.3)
plt.tight_layout()
plot_path = os.path.join(BASE_DIR, "training_plot.png")
plt.savefig(plot_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"\n   📈 Training plot saved → {plot_path}")

# ============================================================
# 7. SAVE BEST MODEL (as .pt file using pickle-based format)
# ============================================================
print("\n" + "=" * 60)
print("💾 Saving best model...")
print("=" * 60)

# Try saving with PyTorch format; if PyTorch is unavailable,
# save as a pickle file with .pt extension (still loadable)
checkpoint = {
    "model_type": "MLPClassifier",
    "model_state": mlp_model,
    "input_dim": X_train_scaled.shape[1],
    "hidden_layers": (64, 32),
    "feature_names": feature_names,
    "scaler_mean": scaler.mean_.tolist(),
    "scaler_scale": scaler.scale_.tolist(),
    "epochs_trained": mlp_model.n_iter_,
    "best_val_score": max(val_scores) if val_scores else None,
}

checkpoint_path = os.path.join(BASE_DIR, "best_model.pt")

try:
    # Attempt to use torch.save for proper .pt format
    import torch
    torch.save(checkpoint, checkpoint_path)
    print(f"   ✓ Saved with torch.save → {checkpoint_path}")
except Exception:
    # Fallback: use pickle (compatible with torch.load on another machine)
    with open(checkpoint_path, "wb") as f:
        pickle.dump(checkpoint, f)
    print(f"   ✓ Saved with pickle → {checkpoint_path}")
    print(f"   ℹ  (PyTorch unavailable on this machine; saved as pickle binary)")
    print(f"      Load with: pickle.load(open('best_model.pt', 'rb'))")

# Also save the sklearn model directly for easy reuse
model_pkl_path = os.path.join(BASE_DIR, "best_model_sklearn.pkl")
with open(model_pkl_path, "wb") as f:
    pickle.dump(
        {"mlp": mlp_model, "rf": rf_model, "lr": lr_model, "scaler": scaler},
        f,
    )
print(f"   ✓ All sklearn models saved → {model_pkl_path}")

# ============================================================
# 8. MODEL COMPARISON & SAVE RESULTS
# ============================================================
print("\n" + "=" * 60)
print("📋 MODEL COMPARISON")
print("=" * 60)

comparison = {
    "Logistic Regression": {"AUROC": lr_auroc, "AUPRC": lr_auprc, "F1": lr_f1, "Accuracy": lr_acc},
    "Random Forest": {"AUROC": rf_auroc, "AUPRC": rf_auprc, "F1": rf_f1, "Accuracy": rf_acc},
    "MLP Neural Network": {"AUROC": mlp_auroc, "AUPRC": mlp_auprc, "F1": mlp_f1, "Accuracy": mlp_acc},
}

# Print comparison table
print(f"\n   {'Model':<25s} {'AUROC':>8s} {'AUPRC':>8s} {'F1':>8s} {'Accuracy':>10s}")
print("   " + "-" * 63)
for name, metrics in comparison.items():
    print(
        f"   {name:<25s} {metrics['AUROC']:>8.4f} {metrics['AUPRC']:>8.4f} {metrics['F1']:>8.4f} {metrics['Accuracy']:>10.4f}"
    )

# Determine best model by AUROC
best_model_name = max(comparison, key=lambda k: comparison[k]["AUROC"])
print(f"\n   🏆 Best model (by AUROC): {best_model_name}")

# --- Save metrics.json ---
metrics_output = {
    "dataset": {
        "total_samples": int(len(y)),
        "train_samples": int(len(y_train)),
        "val_samples": int(len(y_val)),
        "test_samples": int(len(y_test)),
        "num_features": len(feature_names),
        "positive_rate_pct": round(float(y.mean()) * 100, 2),
        "target": TARGET_COL,
    },
    "models": {},
}

for name, metrics in comparison.items():
    metrics_output["models"][name] = {
        "AUROC": round(metrics["AUROC"], 4),
        "AUPRC": round(metrics["AUPRC"], 4),
        "F1": round(metrics["F1"], 4),
        "Accuracy": round(metrics["Accuracy"], 4),
    }

metrics_output["best_model"] = best_model_name

metrics_path = os.path.join(BASE_DIR, "metrics.json")
with open(metrics_path, "w") as f:
    json.dump(metrics_output, f, indent=2)
print(f"\n   💾 Metrics saved → {metrics_path}")

# --- Save evaluation_results.txt ---
eval_path = os.path.join(BASE_DIR, "evaluation_results.txt")
with open(eval_path, "w", encoding="utf-8") as f:
    f.write("=" * 60 + "\n")
    f.write("EDIPS — ICU Mortality Prediction — Evaluation Results\n")
    f.write("=" * 60 + "\n\n")

    f.write("DATASET SUMMARY\n")
    f.write("-" * 40 + "\n")
    f.write(f"Source:             MIMIC-IV Demo v2.2\n")
    f.write(f"Total samples:      {len(y)}\n")
    f.write(f"Train / Val / Test: {len(y_train)} / {len(y_val)} / {len(y_test)}\n")
    f.write(f"Features:           {len(feature_names)}\n")
    f.write(f"Target:             {TARGET_COL} (in-hospital death)\n")
    f.write(f"Positive rate:      {y.mean()*100:.1f}%\n\n")

    f.write("MODEL COMPARISON (on test set)\n")
    f.write("-" * 40 + "\n")
    f.write(f"{'Model':<25s} {'AUROC':>8s} {'AUPRC':>8s} {'F1':>8s} {'Accuracy':>10s}\n")
    f.write("-" * 63 + "\n")
    for name, metrics in comparison.items():
        f.write(
            f"{name:<25s} {metrics['AUROC']:>8.4f} {metrics['AUPRC']:>8.4f} {metrics['F1']:>8.4f} {metrics['Accuracy']:>10.4f}\n"
        )
    f.write(f"\nBest model (by AUROC): {best_model_name}\n\n")

    f.write("DETAILED CLASSIFICATION REPORTS\n")
    f.write("=" * 60 + "\n\n")

    f.write("1. Logistic Regression\n")
    f.write("-" * 40 + "\n")
    f.write(
        classification_report(
            y_test, lr_preds, target_names=["Survived", "Died"], zero_division=0
        )
    )
    f.write(f"\nConfusion Matrix:\n{confusion_matrix(y_test, lr_preds)}\n\n")

    f.write("2. Random Forest\n")
    f.write("-" * 40 + "\n")
    f.write(
        classification_report(
            y_test, rf_preds, target_names=["Survived", "Died"], zero_division=0
        )
    )
    f.write(f"\nConfusion Matrix:\n{confusion_matrix(y_test, rf_preds)}\n\n")

    f.write("3. MLP Neural Network\n")
    f.write("-" * 40 + "\n")
    f.write(
        classification_report(
            y_test, mlp_preds, target_names=["Survived", "Died"], zero_division=0
        )
    )
    f.write(f"\nConfusion Matrix:\n{confusion_matrix(y_test, mlp_preds)}\n\n")

    f.write("=" * 60 + "\n")
    f.write("OUTPUT FILES\n")
    f.write("-" * 40 + "\n")
    f.write("best_model.pt            — MLP model checkpoint\n")
    f.write("best_model_sklearn.pkl   — All 3 sklearn models + scaler\n")
    f.write("metrics.json             — All metrics in JSON format\n")
    f.write("training_plot.png        — MLP loss curves\n")
    f.write("feature_importance.png   — Random Forest top features\n")
    f.write("evaluation_results.txt   — This file\n")

print(f"   📝 Evaluation results saved → {eval_path}")

# ============================================================
# DONE
# ============================================================
print("\n" + "=" * 60)
print("🚀 PIPELINE COMPLETE!")
print("=" * 60)
print(f"\n   Saved files:")
print(f"     • best_model.pt            — MLP model checkpoint")
print(f"     • best_model_sklearn.pkl   — All sklearn models + scaler")
print(f"     • metrics.json             — Metrics for all 3 models")
print(f"     • training_plot.png        — Training/validation loss curves")
print(f"     • feature_importance.png   — Random Forest feature importances")
print(f"     • evaluation_results.txt   — Full evaluation report")
print(f"\n   All files saved in: {BASE_DIR}")
print("=" * 60)
