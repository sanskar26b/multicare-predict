import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os
import logging
from preprocessing.config import TRAINING_READY_PATH, PROCESSED_DATA_PATH, IQR_THRESHOLD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_missing_values(df):
    """
    Handle missing values based on feature type.
    """
    logging.info("Handling missing values...")
    
    # 1. Numerical features -> Mean imputation
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    
    # Note: For time-series, forward fill is often better, but here we apply it generally
    # to columns that might be time-indexed if sorted correctly.
    # In this tabular view, we stick to mean/mode as requested or common practice.
    # But as per instruction: Time-series vitals -> forward fill
    # We'll assume vitals are the numeric ones besides IDs.
    vitals_cols = [col for col in numeric_cols if col not in ['subject_id', 'hadm_id', 'label']]
    df[vitals_cols] = df[vitals_cols].ffill()
    
    # 2. Categorical -> Most frequent
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns
    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")
        
    return df

def handle_outliers(df):
    """
    Detect and clip outliers using the IQR method.
    """
    logging.info("Detecting and clipping outliers (IQR method)...")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    # Avoid clipping IDs or labels
    feature_cols = [col for col in numeric_cols if col not in ['subject_id', 'hadm_id', 'label']]
    
    for col in feature_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - IQR_THRESHOLD * IQR
        upper_bound = Q3 + IQR_THRESHOLD * IQR
        
        df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
    return df

def scale_features(df):
    """
    Apply StandardScaler to numeric columns.
    """
    logging.info("Scaling numeric features...")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    # Don't scale IDs or the target label
    feature_cols = [col for col in numeric_cols if col not in ['subject_id', 'hadm_id', 'label']]
    
    scaler = StandardScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    
    return df

def preprocess_data():
    """
    Main preprocessing pipeline.
    """
    if not os.path.exists(TRAINING_READY_PATH):
        logging.error(f"Dataset not found at {TRAINING_READY_PATH}")
        return
    
    df = pd.read_csv(TRAINING_READY_PATH)
    
    # Run pipeline steps
    df = handle_missing_values(df)
    df = handle_outliers(df)
    df = scale_features(df)
    
    # Save processed dataset
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    logging.info(f"Processed data saved to {PROCESSED_DATA_PATH}")
    return df

if __name__ == "__main__":
    preprocess_data()
