import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from preprocessing.config import TRAINING_READY_PATH, MISSING_VALUES_PLOT, FEATURE_DIST_PLOT, EDA_SUMMARY_TXT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def perform_eda(df):
    """
    Performs Exploratory Data Analysis on the provided dataframe.
    """
    logging.info("Starting EDA...")
    
    # 1. Dataset Info
    info_str = f"Dataset Info:\n"
    info_str += f"Rows: {df.shape[0]}\n"
    info_str += f"Columns: {df.shape[1]}\n"
    info_str += f"Column Names: {df.columns.tolist()}\n"
    info_str += f"Data Types:\n{df.dtypes}\n\n"
    
    # 2. Summary Statistics
    summary_stats = df.describe().T
    info_str += f"Summary Statistics:\n{summary_stats}\n\n"
    
    # 3. Missing Value Analysis
    missing_data = df.isnull().sum()
    missing_percent = (missing_data / len(df)) * 100
    missing_table = pd.concat([missing_data, missing_percent], axis=1, keys=['Total', 'Percent'])
    info_str += f"Missing Values Analysis:\n{missing_table}\n"
    
    # 4. Save Text Summary
    with open(EDA_SUMMARY_TXT, 'w') as f:
        f.write(info_str)
    logging.info(f"EDA summary saved to {EDA_SUMMARY_TXT}")
    
    # 5. Missing Values Heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
    plt.title('Missing Values Heatmap')
    plt.savefig(MISSING_VALUES_PLOT)
    plt.close()
    logging.info(f"Missing values heatmap saved to {MISSING_VALUES_PLOT}")
    
    # 6. Feature Distributions
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    n_cols = 3
    n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
    
    plt.figure(figsize=(20, 5 * n_rows))
    for i, col in enumerate(numeric_cols):
        plt.subplot(n_rows, n_cols, i + 1)
        sns.histplot(df[col].dropna(), kde=True)
        plt.title(f'Distribution of {col}')
    
    plt.tight_layout()
    plt.savefig(FEATURE_DIST_PLOT)
    plt.close()
    logging.info(f"Feature distributions saved to {FEATURE_DIST_PLOT}")

def main():
    if not os.path.exists(TRAINING_READY_PATH):
        logging.error(f"Dataset not found at {TRAINING_READY_PATH}")
        # Create a mock dataset for demonstration if it doesn't exist
        logging.info("Creating mock dataset for demonstration...")
        data = {
            'subject_id': range(1, 276),
            'age': np.random.normal(65, 15, 275).clip(18, 100),
            'heart_rate': np.random.normal(80, 20, 275),
            'temperature': np.random.normal(37, 1, 275),
            'category': np.random.choice(['A', 'B', 'C'], 275),
            'label': np.random.randint(0, 2, 275)
        }
        # Inject some missing values
        mock_df = pd.DataFrame(data)
        for col in ['heart_rate', 'temperature']:
            mock_df.loc[mock_df.sample(frac=0.1).index, col] = np.nan
        
        os.makedirs(os.path.dirname(TRAINING_READY_PATH), exist_ok=True)
        mock_df.to_csv(TRAINING_READY_PATH, index=False)
        logging.info(f"Mock dataset created at {TRAINING_READY_PATH}")

    df = pd.read_csv(TRAINING_READY_PATH)
    perform_eda(df)

if __name__ == "__main__":
    main()
