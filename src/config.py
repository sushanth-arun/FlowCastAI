"""
FlowCast AI - Module 1: Predictive Asset Health & Operational Efficiency
Configuration and schema definitions.
"""

from pathlib import Path
from typing import List, Dict, Any

# Base directories
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
ARTIFACTS_DIR: Path = BASE_DIR / "artifacts"

# Primary dataset paths (with root fallback for robust backward compatibility)
_DEFAULT_DATA_PATH = DATA_DIR / "bdt_mba_supplychain_dataset_2024.csv"
DATA_PATH: Path = _DEFAULT_DATA_PATH if _DEFAULT_DATA_PATH.exists() else (BASE_DIR / "bdt_mba_supplychain_dataset_2024.csv")

_DEFAULT_DATACO_PATH = DATA_DIR / "DataCoSupplyChainDataset.csv"
DATACO_DATA_PATH: Path = _DEFAULT_DATACO_PATH if _DEFAULT_DATACO_PATH.exists() else (BASE_DIR / "DataCoSupplyChainDataset.csv")

DATACO_DESC_PATH: Path = DATA_DIR / "DescriptionDataCoSupplyChain.csv"

# Artifact file paths
MAPPER_PATH: Path = ARTIFACTS_DIR / "mapper.joblib"
ONNX_MODEL_PATH: Path = ARTIFACTS_DIR / "model1_health.onnx"
XGB_MODEL_PATH: Path = ARTIFACTS_DIR / "model_xgb.joblib"
METADATA_PATH: Path = ARTIFACTS_DIR / "model_metadata.json"

# Column schema definitions
TARGET_COL: str = "SupplyChain_Efficiency_Label"
ID_COL: str = "Asset_ID"

RAW_TIMESTAMP_COL: str = "Timestamp"
RAW_MAINTENANCE_COL: str = "Last_Maintenance"

# Continuous numerical features
CONTINUOUS_FEATURES: List[str] = [
    "Temperature",
    "Vibration",
    "Condition_Score",
    "Resource_Utilization",
    "Delivery_Efficiency",
    "Downtime_Hours",
    "Logistics_Cost",
    "Days_Since_Maintenance"
]

# Categorical features
ORDINAL_FEATURE: str = "Inventory_Level"
INVENTORY_CATEGORIES: List[str] = ["Low", "Medium", "High"]

CATEGORICAL_ONEHOT_FEATURES: List[str] = [
    "Location",
    "Event_Hour",
    "Event_DayOfWeek"
]

# Target label human-readable mapping and risk thresholds
LABEL_MAPPING: Dict[int, Dict[str, Any]] = {
    0: {
        "name": "Optimal Efficiency",
        "description": "Standard operational performance, low disruption risk",
        "risk_level": "LOW",
        "flag_failure_risk": False
    },
    1: {
        "name": "Sub-Optimal / Strained",
        "description": "Degraded efficiency, elevated logistics strain or maintenance lag",
        "risk_level": "MODERATE",
        "flag_failure_risk": False
    },
    2: {
        "name": "High Risk Asset Degradation",
        "description": "Severe efficiency breakdown, critical failure probability flagged",
        "risk_level": "CRITICAL",
        "flag_failure_risk": True
    }
}

# Telemetry anomaly thresholds for risk monitoring
CRITICAL_THRESHOLDS: Dict[str, float] = {
    "temperature_max": 42.0,
    "vibration_max": 4.0,
    "condition_score_min": 60.0,
    "downtime_hours_max": 6.0
}
