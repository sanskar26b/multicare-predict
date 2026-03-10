"""
EDIPS — Full Pipeline Orchestrator
====================================
Runs the entire pipeline from raw MIMIC-IV CSVs to a running
FastAPI + React system.

Usage:
    python run_pipeline.py [--step STEP]

Steps:
    1  prepare   — raw CSVs → training_ready/training_set.csv
    2  xai       — EDA + preprocess + sliding windows (xai/)
    3  train     — train LR/RF/MLP models → best_model_sklearn.pkl
    4  backend   — install deps and start FastAPI on :8000
    5  frontend  — install deps and start Vite dev server on :5173

Run all:
    python run_pipeline.py
"""

import subprocess
import sys
import os
import argparse

BASE = os.path.dirname(os.path.abspath(__file__))


def run(cmd, cwd=None, check=True):
    print(f"\n$ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(
        cmd, cwd=cwd or BASE, shell=isinstance(cmd, str), check=False
    )
    if check and result.returncode != 0:
        print(f"[ERROR] Step failed (exit {result.returncode})")
        sys.exit(result.returncode)
    return result.returncode


def step_prepare():
    print("\n" + "=" * 60)
    print("STEP 1: Prepare training data")
    print("=" * 60)
    run([sys.executable, "prepare_training_data.py"])


def step_xai():
    print("\n" + "=" * 60)
    print("STEP 2: XAI — EDA + preprocess + sliding windows")
    print("=" * 60)
    xai_dir = os.path.join(BASE, "xai")
    run([sys.executable, "scripts/run_pipeline.py"], cwd=xai_dir)


def step_train():
    print("\n" + "=" * 60)
    print("STEP 3: Train models")
    print("=" * 60)
    run([sys.executable, "train_pipeline.py"])


def step_backend():
    print("\n" + "=" * 60)
    print("STEP 4: Backend — install deps + start FastAPI")
    print("=" * 60)
    backend_dir = os.path.join(BASE, "backend")
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"], cwd=backend_dir)
    print("\nStarting FastAPI on http://localhost:8000 ...")
    print("Press Ctrl+C to stop.")
    run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        cwd=backend_dir, check=False)


def step_frontend():
    print("\n" + "=" * 60)
    print("STEP 5: Frontend — install deps + start Vite")
    print("=" * 60)
    fe_dir = os.path.join(BASE, "frontend")
    run("npm install", cwd=fe_dir)
    print("\nStarting Vite dev server on http://localhost:5173 ...")
    print("Press Ctrl+C to stop.")
    run("npm run dev", cwd=fe_dir, check=False)


STEPS = {
    "prepare":  step_prepare,
    "xai":      step_xai,
    "train":    step_train,
    "backend":  step_backend,
    "frontend": step_frontend,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EDIPS pipeline orchestrator")
    parser.add_argument("--step", choices=list(STEPS.keys()),
                        help="Run only a specific step")
    args = parser.parse_args()

    if args.step:
        STEPS[args.step]()
    else:
        # Steps 1-3 are sequential (data → model)
        # Steps 4-5 need to run in separate terminals
        for name in ["prepare", "xai", "train"]:
            STEPS[name]()
        print("\n" + "=" * 60)
        print("Pipeline steps 1-3 complete!")
        print("=" * 60)
        print("\nTo start the full system, open TWO terminals and run:")
        print("  Terminal 1: python run_pipeline.py --step backend")
        print("  Terminal 2: python run_pipeline.py --step frontend")
        print("\nThen open http://localhost:5173 in your browser.")
