"""
FinGuard - Data Collection & Preprocessing Pipeline
===================================================
Provides modular, zero-leakage data acquisition, validation, 
and preprocessing for the Taiwanese Bankruptcy Prediction benchmark.
"""

import os
import io
import zipfile
import logging
from typing import Tuple, Dict, Any, Optional
import requests
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
import joblib

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants and Citations
UCI_DATASET_URL = "https://archive.ics.uci.edu/static/public/572/taiwanese+bankruptcy+prediction.zip"
RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
RAW_CSV_PATH = os.path.join(RAW_DATA_DIR, "taiwanese_bankruptcy.csv")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.joblib")


def ensure_directories():
    """Ensure raw, processed, and model directories exist."""
    for path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
        os.makedirs(path, exist_ok=True)


def download_uci_dataset(force_download: bool = False) -> str:
    """
    Download the authentic Taiwanese Bankruptcy dataset from the official UCI Machine Learning Repository.
    Caches the extracted CSV in data/raw/taiwanese_bankruptcy.csv.

    Citation:
    - Dataset: Taiwanese Bankruptcy Prediction (UCI ID: 572)
    - Source: Taiwan Economic Journal (1999-2009)
    - Authors: Der-Sheng Liang, Chi-Jie Lu, Chih-Fong Tsai
    - License: CC BY 4.0
    """
    ensure_directories()

    if os.path.exists(RAW_CSV_PATH) and not force_download:
        logger.info(f"Dataset already cached at: {RAW_CSV_PATH}")
        return RAW_CSV_PATH

    logger.info(f"Downloading authentic dataset from UCI: {UCI_DATASET_URL}")
    try:
        response = requests.get(UCI_DATASET_URL, timeout=60)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Look for the data file
            csv_candidates = [name for name in z.namelist() if name.endswith(".csv")]
            if not csv_candidates:
                raise ValueError("No CSV file found inside the UCI zip archive.")
            
            target_csv = csv_candidates[0]
            logger.info(f"Extracting {target_csv} to {RAW_CSV_PATH}...")
            with open(RAW_CSV_PATH, "wb") as f_out:
                f_out.write(z.read(target_csv))

        logger.info("Download and extraction successful.")
        return RAW_CSV_PATH

    except Exception as e:
        logger.error(f"Failed to download automatically from UCI: {e}")
        logger.info(
            "\n[MANUAL DOWNLOAD INSTRUCTIONS]:\n"
            "1. Visit https://archive.ics.uci.edu/dataset/572/taiwanese+bankruptcy+prediction\n"
            "2. Download 'taiwanese+bankruptcy+prediction.zip'\n"
            "3. Extract 'data.csv' and place it at: data/raw/taiwanese_bankruptcy.csv\n"
        )
        raise e


def load_and_clean_raw_data(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load raw CSV, clean column names by stripping whitespace,
    and remove duplicate rows if present.
    """
    if csv_path is None:
        csv_path = RAW_CSV_PATH

    if not os.path.exists(csv_path):
        download_uci_dataset()

    df = pd.read_csv(csv_path)

    # Clean whitespace from column names (UCI dataset has leading spaces in column headers)
    df.columns = [c.strip() for c in df.columns]

    # Check and remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    deduped_rows = len(df)
    if initial_rows != deduped_rows:
        logger.info(f"Removed {initial_rows - deduped_rows} duplicate rows.")

    return df


def inspect_data_quality(df: pd.DataFrame, target_col: str = "Bankrupt?") -> Dict[str, Any]:
    """
    Perform rigorous data quality validation:
    - Missing value detection
    - Infinite value detection
    - Target distribution & imbalance ratio
    - Feature count & data types
    """
    total_rows, total_cols = df.shape
    missing_counts = df.isnull().sum()
    total_missing = int(missing_counts.sum())
    
    # Check for infinite numbers
    numeric_df = df.select_dtypes(include=[np.number])
    inf_counts = int(np.isinf(numeric_df.values).sum())

    # Target class distribution
    if target_col in df.columns:
        target_counts = df[target_col].value_counts().to_dict()
        non_bankrupt = target_counts.get(0, 0)
        bankrupt = target_counts.get(1, 0)
        imbalance_ratio = non_bankrupt / max(bankrupt, 1)
        bankruptcy_rate = (bankrupt / total_rows) * 100
    else:
        target_counts = {}
        imbalance_ratio = 0.0
        bankruptcy_rate = 0.0

    report = {
        "total_rows": total_rows,
        "total_features": total_cols - (1 if target_col in df.columns else 0),
        "total_missing_values": total_missing,
        "infinite_values": inf_counts,
        "class_distribution": target_counts,
        "imbalance_ratio": round(imbalance_ratio, 2),
        "bankruptcy_rate_pct": round(bankruptcy_rate, 2),
    }

    logger.info(f"Data Quality Report: {report}")
    return report


def build_preprocessor() -> Pipeline:
    """
    Construct a zero-data-leakage preprocessing pipeline.
    Uses:
    1. SimpleImputer(strategy='median') - Robust to extreme financial outliers
    2. RobustScaler() - Centers using median and scales using IQR, essential for skewed financial ratios
    """
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", RobustScaler(with_centering=True, with_scaling=True, unit_variance=False)),
    ])


def prepare_train_test_split(
    df: pd.DataFrame,
    target_col: str = "Bankrupt?",
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, Pipeline]:
    """
    Split features and target with strict zero-leakage guarantee.
    
    Time-aware limitation note:
    The UCI Taiwanese dataset spans 1999-2009 annual filings but individual company fiscal-year 
    timestamps are omitted in the original released dataset. As per Section 3.A, we document this 
    explicit limitation and utilize a Stratified Shuffle Split to preserve the exact default prevalence
    across both train and test partitions without leaking test distributions.
    """
    ensure_directories()

    X = df.drop(columns=[target_col])
    y = df[target_col].astype(int)

    # Stratified split ensures test set accurately reflects the 3.2% bankruptcy rate
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Build and fit preprocessing pipeline STRICTLY on X_train to prevent leakage
    preprocessor = build_preprocessor()
    logger.info("Fitting preprocessor STRICTLY on X_train (Zero Data Leakage)...")
    preprocessor.fit(X_train)

    # Save fitted preprocessor
    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    logger.info(f"Fitted preprocessor saved to {PREPROCESSOR_PATH}")

    # Persist processed partitions for reproducible training & evaluation
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)

    train_path = os.path.join(PROCESSED_DATA_DIR, "train.csv")
    test_path = os.path.join(PROCESSED_DATA_DIR, "test.csv")

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    logger.info(f"Train partition ({train_df.shape}) saved to {train_path}")
    logger.info(f"Test partition ({test_df.shape}) saved to {test_path}")

    return X_train, X_test, y_train, y_test, preprocessor


def run_pipeline() -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, Pipeline, Dict[str, Any]]:
    """Execute the end-to-end data pipeline."""
    logger.info("Starting FinGuard Data Pipeline execution...")
    download_uci_dataset()
    df = load_and_clean_raw_data()
    quality_report = inspect_data_quality(df)
    X_train, X_test, y_train, y_test, preprocessor = prepare_train_test_split(df)
    logger.info("FinGuard Data Pipeline completed successfully.")
    return X_train, X_test, y_train, y_test, preprocessor, quality_report


if __name__ == "__main__":
    run_pipeline()
