import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # xai/
REPO_ROOT = os.path.dirname(BASE_DIR)                                   # repo root
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

# Dataset Paths — training_set.csv lives at repo root, not inside xai/
TRAINING_READY_PATH = os.path.join(REPO_ROOT, 'training_ready', 'training_set.csv')
PROCESSED_DATA_PATH = os.path.join(DATA_DIR, 'processed', 'processed_data.csv')
WINDOWED_DATA_PATH = os.path.join(DATA_DIR, 'processed', 'X.npy')

# EDA Config
MISSING_VALUES_PLOT = os.path.join(REPORTS_DIR, 'missing_values.png')
FEATURE_DIST_PLOT = os.path.join(REPORTS_DIR, 'feature_distributions.png')
EDA_SUMMARY_TXT = os.path.join(REPORTS_DIR, 'eda_summary.txt')

# Preprocessing Config
WINDOW_SIZE = 24
IQR_THRESHOLD = 1.5

# Ensure directory exists if needed
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, 'processed'), exist_ok=True)
