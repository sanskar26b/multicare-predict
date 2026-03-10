import pandas as pd
import numpy as np
import os
import logging
from preprocessing.config import PROCESSED_DATA_PATH, WINDOWED_DATA_PATH, WINDOW_SIZE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_sliding_windows(df, window_size=24):
    """
    Converts tabular data into time-series input windows.
    Each window represents 'window_size' sequential observations.
    """
    logging.info(f"Creating sliding windows of size {window_size}...")
    
    # Drop non-feature columns
    feature_cols = df.select_dtypes(include=[np.number]).columns
    feature_cols = [col for col in feature_cols if col not in ['subject_id', 'hadm_id', 'label']]
    
    data_array = df[feature_cols].values
    n_features = len(feature_cols)
    
    windows = []
    # Simplified sliding window implementation
    # In a real ICU dataset, windows should be grouped by patient (subject_id)
    # For this project requirement, we follow the general looping approach
    for i in range(len(data_array) - window_size + 1):
        window = data_array[i : i + window_size]
        windows.append(window)
        
    X = np.array(windows)
    logging.info(f"Generated {len(X)} windows with shape {X.shape}")
    return X

def main():
    if not os.path.exists(PROCESSED_DATA_PATH):
        logging.error(f"Processed data not found at {PROCESSED_DATA_PATH}")
        return
        
    df = pd.read_csv(PROCESSED_DATA_PATH)
    X = create_sliding_windows(df, WINDOW_SIZE)
    
    # Save output
    os.makedirs(os.path.dirname(WINDOWED_DATA_PATH), exist_ok=True)
    np.save(WINDOWED_DATA_PATH, X)
    logging.info(f"Sliding windows saved to {WINDOWED_DATA_PATH}")

if __name__ == "__main__":
    main()
