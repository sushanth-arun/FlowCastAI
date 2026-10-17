"""
FlowCast AI - DataCo Supply Chain Data Preprocessing Pipeline.

Handles:
1. Parsing 'order date (DateOrders)' and 'shipping date (DateOrders)'.
2. Extracting delta features like 'Scheduled_vs_Real_Shipping_Diff'.
3. Building and fitting two DataFrameMapper instances:
   - mapper_delays: for Module 2 (Logistics & Shipment Delay Prediction).
   - mapper_stock: for Module 3 (Inventory Demand & Stockout Risk).
4. Serialization and inference transformation routines.
"""

from pathlib import Path
from typing import Tuple, List, Optional, Union
import joblib
import numpy as np
import pandas as pd
import sklearn.utils
if not hasattr(sklearn.utils, 'tosequence'):
    sklearn.utils.tosequence = list
from sklearn_pandas import DataFrameMapper
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from src.config import (
    BASE_DIR,
    ARTIFACTS_DIR,
    DATACO_DATA_PATH
)

MAPPER_DELAYS_PATH: Path = ARTIFACTS_DIR / "mapper_delays.joblib"
MAPPER_STOCK_PATH: Path = ARTIFACTS_DIR / "mapper_stock.joblib"

# Module 2 (Delays) feature definitions
DELAYS_NUMERICAL_COLS: List[str] = [
    "Order Item Quantity",
    "Sales"
]
DELAYS_CATEGORICAL_COLS: List[str] = [
    "Shipping Mode",
    "Market",
    "Order Region"
]
DELAYS_TARGET_COL: str = "Late_delivery_risk"

# Module 3 (Stockout & Demand) feature definitions
STOCK_NUMERICAL_COLS: List[str] = [
    "Order Item Discount Rate",
    "Product Price"
]
STOCK_CATEGORICAL_COLS: List[str] = [
    "Category Name",
    "Department Name"
]
STOCK_TARGET_DEMAND_COL: str = "Order Item Quantity"
STOCK_TARGET_STATUS_COL: str = "Product Status"


def parse_dataco_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse order date and shipping date, computing operational deltas.

    Features generated:
        - Scheduled_vs_Real_Shipping_Diff: Real shipping days minus scheduled days.
        - Order_Hour: Hour of day when order was placed.
        - Order_DayOfWeek: Day of week when order was placed (0=Monday, 6=Sunday).

    Args:
        df: Input DataFrame containing raw DataCo columns.

    Returns:
        DataFrame with transformed date and delta features.
    """
    df = df.copy()

    # Parse order date
    if "order date (DateOrders)" in df.columns:
        order_dt = pd.to_datetime(df["order date (DateOrders)"], errors="coerce")
        df["Order_Hour"] = order_dt.dt.hour.fillna(12).astype(int)
        df["Order_DayOfWeek"] = order_dt.dt.dayofweek.fillna(0).astype(int)
    else:
        df["Order_Hour"] = 12
        df["Order_DayOfWeek"] = 0

    # Parse shipping date
    if "shipping date (DateOrders)" in df.columns:
        ship_dt = pd.to_datetime(df["shipping date (DateOrders)"], errors="coerce")
        df["Shipping_Hour"] = ship_dt.dt.hour.fillna(12).astype(int)
        df["Shipping_DayOfWeek"] = ship_dt.dt.dayofweek.fillna(0).astype(int)

    # Compute difference: Days for shipping (real) - Days for shipment (scheduled)
    if "Days for shipping (real)" in df.columns and "Days for shipment (scheduled)" in df.columns:
        real_days = pd.to_numeric(df["Days for shipping (real)"], errors="coerce").fillna(0)
        sched_days = pd.to_numeric(df["Days for shipment (scheduled)"], errors="coerce").fillna(0)
        df["Scheduled_vs_Real_Shipping_Diff"] = real_days - sched_days
    else:
        df["Scheduled_vs_Real_Shipping_Diff"] = 0.0

    return df


def build_delays_mapper() -> DataFrameMapper:
    """
    Construct DataFrameMapper for Module 2 (Delay Risk).

    Encodes:
        - Standard scaling: Order Item Quantity, Sales
        - One-hot encoding: Shipping Mode, Market, Order Region
    """
    mappings = []
    for col in DELAYS_NUMERICAL_COLS:
        mappings.append(([col], StandardScaler()))

    for col in DELAYS_CATEGORICAL_COLS:
        mappings.append(([col], OneHotEncoder(handle_unknown="ignore", sparse_output=False)))

    return DataFrameMapper(mappings, df_out=True)


def build_stock_mapper() -> DataFrameMapper:
    """
    Construct DataFrameMapper for Module 3 (Inventory Demand & Stockout Risk).

    Encodes:
        - Standard scaling: Order Item Discount Rate, Product Price
        - One-hot encoding: Category Name, Department Name
    """
    mappings = []
    for col in STOCK_NUMERICAL_COLS:
        mappings.append(([col], StandardScaler()))

    for col in STOCK_CATEGORICAL_COLS:
        mappings.append(([col], OneHotEncoder(handle_unknown="ignore", sparse_output=False)))

    return DataFrameMapper(mappings, df_out=True)


def load_and_preprocess_dataco(
    sample_size: int = 40000,
    random_seed: int = 42
) -> Tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series, DataFrameMapper, DataFrameMapper]:
    """
    Load DataCo dataset, parse temporal columns, fit mappers, and return
    engineered matrices and targets for Module 2 and Module 3.

    Args:
        sample_size: Number of records to sample for balanced training speed.
        random_seed: Reproducibility seed.

    Returns:
        Tuple containing:
            - df_processed: Processed DataCo DataFrame
            - y_delays: Series for Late_delivery_risk
            - y_demand: Series for Order Item Quantity
            - y_stockout_risk: Binary surge/stockout risk Series (1 if demand >= 4 else 0)
            - mapper_delays: Fitted mapper for Module 2
            - mapper_stock: Fitted mapper for Module 3
    """
    if not DATACO_DATA_PATH.exists():
        raise FileNotFoundError(f"DataCo dataset missing at: {DATACO_DATA_PATH}")

    # Read dataset with latin1 encoding to handle special characters
    df_raw = pd.read_csv(DATACO_DATA_PATH, nrows=sample_size, encoding="latin1")
    df_processed = parse_dataco_temporal_features(df_raw)

    # Module 2 target
    if DELAYS_TARGET_COL not in df_processed.columns:
        raise KeyError(f"Target column '{DELAYS_TARGET_COL}' not in DataCo dataset.")
    y_delays = df_processed[DELAYS_TARGET_COL].astype(int)

    # Module 3 targets
    y_demand = df_processed[STOCK_TARGET_DEMAND_COL].astype(float)
    # Binary stockout surge risk: Orders with quantity >= 4 represent surge depletion risk
    y_stockout_risk = (df_processed[STOCK_TARGET_DEMAND_COL] >= 4).astype(int)

    # Fit mappers
    mapper_delays = build_delays_mapper()
    mapper_delays.fit(df_processed)

    mapper_stock = build_stock_mapper()
    mapper_stock.fit(df_processed)

    return df_processed, y_delays, y_demand, y_stockout_risk, mapper_delays, mapper_stock


def save_dataco_mappers(
    mapper_delays: DataFrameMapper,
    mapper_stock: DataFrameMapper
) -> Tuple[Path, Path]:
    """
    Serialize both DataCo mappers using joblib.
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(mapper_delays, MAPPER_DELAYS_PATH)
    joblib.dump(mapper_stock, MAPPER_STOCK_PATH)
    return MAPPER_DELAYS_PATH, MAPPER_STOCK_PATH


def load_dataco_mappers() -> Tuple[DataFrameMapper, DataFrameMapper]:
    """
    Load pre-fitted mappers from disk.
    """
    if not MAPPER_DELAYS_PATH.exists():
        raise FileNotFoundError(f"Delays mapper not found at {MAPPER_DELAYS_PATH}")
    if not MAPPER_STOCK_PATH.exists():
        raise FileNotFoundError(f"Stock mapper not found at {MAPPER_STOCK_PATH}")

    m_delays = joblib.load(MAPPER_DELAYS_PATH)
    m_stock = joblib.load(MAPPER_STOCK_PATH)
    return m_delays, m_stock


def transform_delays_raw(raw_df: pd.DataFrame, mapper: DataFrameMapper) -> np.ndarray:
    """
    Transform raw incoming logistics payload for Module 2 inference.
    """
    df_engineered = parse_dataco_temporal_features(raw_df)
    transformed = mapper.transform(df_engineered)
    if isinstance(transformed, pd.DataFrame):
        return transformed.values.astype(np.float32)
    return np.asarray(transformed, dtype=np.float32)


def transform_stock_raw(raw_df: pd.DataFrame, mapper: DataFrameMapper) -> np.ndarray:
    """
    Transform raw incoming product/catalog payload for Module 3 inference.
    """
    transformed = mapper.transform(raw_df)
    if isinstance(transformed, pd.DataFrame):
        return transformed.values.astype(np.float32)
    return np.asarray(transformed, dtype=np.float32)


if __name__ == "__main__":
    print("Testing DataCo preprocessing pipeline...")
    df_p, y_del, y_dem, y_stk, m_del, m_stk = load_and_preprocess_dataco(sample_size=5000)
    print(f"Dataset processed rows: {len(df_p)}")
    print(f"Delays features shape:  {m_del.transform(df_p).shape}")
    print(f"Stock features shape:   {m_stk.transform(df_p).shape}")
    print("[OK] Preprocessing test passed without overwriting production artifacts.")
