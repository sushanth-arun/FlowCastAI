"""
FlowCast AI - Data Preprocessing & Feature Engineering Pipeline.

Handles:
1. Timestamp & maintenance interval parsing.
2. Construction of sklearn-pandas DataFrameMapper.
3. Scaling, ordinal encoding, and one-hot encoding.
4. Production serialization and deserialization of the fitted mapper.
"""

from pathlib import Path
from typing import List, Tuple, Optional, Union
import joblib
import numpy as np
import pandas as pd
import sklearn.utils
if not hasattr(sklearn.utils, 'tosequence'):
    sklearn.utils.tosequence = list
from sklearn_pandas import DataFrameMapper
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder

from src.config import (
    DATA_PATH,
    TARGET_COL,
    ID_COL,
    RAW_TIMESTAMP_COL,
    RAW_MAINTENANCE_COL,
    CONTINUOUS_FEATURES,
    ORDINAL_FEATURE,
    INVENTORY_CATEGORIES,
    CATEGORICAL_ONEHOT_FEATURES,
    MAPPER_PATH,
)


def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract temporal delta features from Timestamp and Last_Maintenance columns.

    Features generated:
        - Days_Since_Maintenance: Float days elapsed between maintenance and event.
        - Event_Hour: Hour of day (0-23).
        - Event_DayOfWeek: Day of week (0=Monday, 6=Sunday).

    Args:
        df: Input DataFrame containing raw timestamp columns.

    Returns:
        DataFrame with engineered temporal features appended.
    """
    df = df.copy()

    # Parse timestamps with fallback formats for robustness
    if RAW_TIMESTAMP_COL in df.columns:
        ts = pd.to_datetime(df[RAW_TIMESTAMP_COL], format='%d-%m-%Y %H:%M', errors='coerce')
        if ts.isna().all():
            ts = pd.to_datetime(df[RAW_TIMESTAMP_COL], errors='coerce')
        df['Event_Hour'] = ts.dt.hour.fillna(12).astype(int)
        df['Event_DayOfWeek'] = ts.dt.dayofweek.fillna(0).astype(int)
    else:
        df['Event_Hour'] = 12
        df['Event_DayOfWeek'] = 0
        ts = pd.Series([pd.Timestamp.now()] * len(df))

    if RAW_MAINTENANCE_COL in df.columns:
        maint = pd.to_datetime(df[RAW_MAINTENANCE_COL], format='%d-%m-%Y', errors='coerce')
        if maint.isna().all():
            maint = pd.to_datetime(df[RAW_MAINTENANCE_COL], errors='coerce')
    else:
        maint = ts

    # Compute delta in days
    delta_days = (ts - maint).dt.total_seconds() / (24.0 * 3600.0)
    df['Days_Since_Maintenance'] = delta_days.fillna(0.0).astype(float)

    return df


def build_feature_mapper() -> DataFrameMapper:
    """
    Construct an sklearn-pandas DataFrameMapper with standard scaling,
    ordinal encoding, and one-hot encoding specifications.

    Returns:
        Unfitted DataFrameMapper instance configured for FlowCast telemetry.
    """
    feature_mappings = []

    # 1. Standard Scaling for each continuous telemetry and operational metric
    for col in CONTINUOUS_FEATURES:
        feature_mappings.append(([col], StandardScaler()))

    # 2. Ordinal encoding for Inventory_Level (Low -> 0, Medium -> 1, High -> 2)
    feature_mappings.append(
        (
            [ORDINAL_FEATURE],
            OrdinalEncoder(
                categories=[INVENTORY_CATEGORIES],
                handle_unknown='use_encoded_value',
                unknown_value=-1
            )
        )
    )

    # 3. One-hot encoding for Location and temporal attributes
    for col in CATEGORICAL_ONEHOT_FEATURES:
        feature_mappings.append(
            (
                [col],
                OneHotEncoder(
                    handle_unknown='ignore',
                    sparse_output=False
                )
            )
        )

    mapper = DataFrameMapper(feature_mappings, df_out=True)
    return mapper


def load_and_preprocess_data(
    file_path: Optional[Union[str, Path]] = None
) -> Tuple[pd.DataFrame, pd.Series, DataFrameMapper, List[str]]:
    """
    Load raw CSV data, perform feature engineering, fit DataFrameMapper,
    and return transformed features and target vector.

    Args:
        file_path: Optional path to CSV dataset. Defaults to DATA_PATH in config.

    Returns:
        Tuple containing:
            - X_df: Transformed features as DataFrame.
            - y: Target series (SupplyChain_Efficiency_Label).
            - mapper: Fitted DataFrameMapper instance.
            - feature_names: List of transformed feature names.
    """
    dataset_path = Path(file_path) if file_path else DATA_PATH
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at expected path: {dataset_path}")

    df_raw = pd.read_csv(dataset_path)

    # Extract temporal features
    df_engineered = extract_temporal_features(df_raw)

    # Separate target
    if TARGET_COL not in df_engineered.columns:
        raise KeyError(f"Target column '{TARGET_COL}' missing from input dataset.")

    y = df_engineered[TARGET_COL].astype(int)

    # Fit feature mapper
    mapper = build_feature_mapper()
    X_transformed = mapper.fit_transform(df_engineered)

    feature_names = list(X_transformed.columns)

    return X_transformed, y, mapper, feature_names


def transform_raw_data(
    raw_df: pd.DataFrame,
    mapper: DataFrameMapper
) -> np.ndarray:
    """
    Transform raw incoming inference DataFrame using a pre-fitted mapper.

    Args:
        raw_df: Raw input DataFrame matching schema.
        mapper: Fitted DataFrameMapper instance.

    Returns:
        Transformed 2D numpy array ready for model inference.
    """
    df_engineered = extract_temporal_features(raw_df)
    transformed = mapper.transform(df_engineered)
    if isinstance(transformed, pd.DataFrame):
        return transformed.values.astype(np.float32)
    return np.asarray(transformed, dtype=np.float32)


def save_mapper(mapper: DataFrameMapper, filepath: Optional[Union[str, Path]] = None) -> Path:
    """
    Serialize fitted DataFrameMapper to disk using joblib.

    Args:
        mapper: Fitted DataFrameMapper instance.
        filepath: Optional destination path. Defaults to MAPPER_PATH.

    Returns:
        Path where mapper artifact was saved.
    """
    save_path = Path(filepath) if filepath else MAPPER_PATH
    save_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(mapper, save_path)
    return save_path


def load_mapper(filepath: Optional[Union[str, Path]] = None) -> DataFrameMapper:
    """
    Load a serialized DataFrameMapper from disk.

    Args:
        filepath: Optional path to serialized mapper. Defaults to MAPPER_PATH.

    Returns:
        Fitted DataFrameMapper instance.
    """
    load_path = Path(filepath) if filepath else MAPPER_PATH
    if not load_path.exists():
        raise FileNotFoundError(f"Serialized mapper not found at: {load_path}")
    return joblib.load(load_path)


if __name__ == "__main__":
    print("Testing data preprocessing pipeline...")
    X_trans, y_labels, fit_mapper, feat_names = load_and_preprocess_data()
    print(f"Preprocessed X shape: {X_trans.shape}")
    print(f"Preprocessed y shape: {y_labels.shape}")
    print(f"Feature count: {len(feat_names)}")
    print(f"First 10 features: {feat_names[:10]}")

    # Test serialization
    saved_path = save_mapper(fit_mapper)
    print(f"Fitted mapper saved successfully to: {saved_path}")

    # Test reloading
    reloaded_mapper = load_mapper(saved_path)
    test_transformed = transform_raw_data(pd.read_csv(DATA_PATH).head(3), reloaded_mapper)
    print(f"Reload test transformed shape: {test_transformed.shape}")
    print("Data preprocessing module check passed!")
