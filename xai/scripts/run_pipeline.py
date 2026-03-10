import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.eda import perform_eda
from preprocessing.preprocess import preprocess_data
from preprocessing.create_windows import create_sliding_windows
from preprocessing.config import TRAINING_READY_PATH, WINDOW_SIZE, WINDOWED_DATA_PATH

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline():
    """
    Runs the full EDIPS preprocessing pipeline sequentially.
    """
    logging.info("==========================================")
    logging.info("EDIPS PREPROCESSING PIPELINE STARTING")
    logging.info("==========================================")
    
    import pandas as pd
    
    # 1. Check/Generate Data
    if not os.path.exists(TRAINING_READY_PATH):
        logging.info("Source data not found. Running EDA to generate mock data...")
        from preprocessing.eda import main as eda_main
        eda_main()
    
    df = pd.read_csv(TRAINING_READY_PATH)
    
    # 2. EDA
    logging.info("\n--- PHASE 1: EXPLORATORY DATA ANALYSIS ---")
    perform_eda(df)
    
    # 3. Preprocessing
    logging.info("\n--- PHASE 2: PREPROCESSING ---")
    processed_df = preprocess_data()
    
    # 4. Window Generation
    logging.info("\n--- PHASE 3: SLIDING WINDOW GENERATION ---")
    if processed_df is not None:
        X = create_sliding_windows(processed_df, WINDOW_SIZE)
        import numpy as np
        os.makedirs(os.path.dirname(WINDOWED_DATA_PATH), exist_ok=True)
        np.save(WINDOWED_DATA_PATH, X)
        logging.info(f"Final ML-ready dataset saved to {WINDOWED_DATA_PATH}")

    logging.info("==========================================")
    logging.info("EDIPS PREPROCESSING PIPELINE COMPLETED")
    logging.info("==========================================")

if __name__ == "__main__":
    run_pipeline()
