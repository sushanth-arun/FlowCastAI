"""
FlowCast AI - End-to-End Inference Verification Engine.

Loads:
- artifacts/mapper.joblib
- artifacts/model1_efficiency.onnx
- artifacts/model_metadata.json

Accepts raw JSON dictionary payloads or Pandas DataFrame rows, executes full
preprocessing, performs ONNX Runtime inference, and returns predicted efficiency labels,
confidence distributions, and asset failure risk alerts.
"""

from pathlib import Path
from typing import Dict, Any, List, Union, Optional
import json
import joblib
import numpy as np
import pandas as pd
import onnxruntime as ort

from src.config import (
    DATA_PATH,
    MAPPER_PATH,
    ONNX_MODEL_PATH,
    METADATA_PATH,
    LABEL_MAPPING,
    CRITICAL_THRESHOLDS
)
from src.data.preprocess import extract_temporal_features


class FlowCastEfficiencyPredictor:
    """
    Production Inference Engine for FlowCast AI Module 1.
    """

    def __init__(
        self,
        mapper_path: Optional[Union[str, Path]] = None,
        onnx_model_path: Optional[Union[str, Path]] = None,
        metadata_path: Optional[Union[str, Path]] = None
    ):
        """
        Initialize the predictor by loading serialized pipeline artifacts.

        Args:
            mapper_path: Path to serialized DataFrameMapper (.joblib).
            onnx_model_path: Path to serialized ONNX neural network (.onnx).
            metadata_path: Path to pipeline metadata (.json).
        """
        self.mapper_path = Path(mapper_path) if mapper_path else MAPPER_PATH
        self.onnx_model_path = Path(onnx_model_path) if onnx_model_path else ONNX_MODEL_PATH
        self.metadata_path = Path(metadata_path) if metadata_path else METADATA_PATH

        if not self.mapper_path.exists():
            raise FileNotFoundError(f"Mapper artifact missing: {self.mapper_path}. Run export.py first.")
        if not self.onnx_model_path.exists():
            raise FileNotFoundError(f"ONNX model artifact missing: {self.onnx_model_path}. Run export.py first.")

        # 1. Load fitted DataFrameMapper
        self.mapper = joblib.load(self.mapper_path)

        # 2. Initialize ONNX Runtime session
        self.ort_session = ort.InferenceSession(
            str(self.onnx_model_path),
            providers=["CPUExecutionProvider"]
        )
        self.input_name = self.ort_session.get_inputs()[0].name
        self.output_name = self.ort_session.get_outputs()[0].name

        # 3. Load optional metadata
        self.metadata = {}
        if self.metadata_path.exists():
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

        self.label_info = LABEL_MAPPING
        self.thresholds = CRITICAL_THRESHOLDS

    def _assess_asset_risk(self, row: pd.Series, predicted_label: int) -> Dict[str, Any]:
        """
        Assess asset health failure risk based on predicted efficiency class
        and telemetry threshold violations.

        Args:
            row: Pandas Series representing the raw input row.
            predicted_label: Predicted integer label (0, 1, 2).

        Returns:
            Dict containing risk flag, severity level, and specific risk triggers.
        """
        risk_triggers: List[str] = []

        temp = float(row.get("Temperature", 0.0))
        vib = float(row.get("Vibration", 0.0))
        cond = float(row.get("Condition_Score", 100.0))
        downtime = float(row.get("Downtime_Hours", 0.0))

        temp_str = f"{temp:.2f} deg C"
        if temp > self.thresholds["temperature_max"]:
            risk_triggers.append(f"High Temperature ({temp_str} > {self.thresholds['temperature_max']} deg C)")
        if vib > self.thresholds["vibration_max"]:
            risk_triggers.append(f"Elevated Vibration ({vib:.2f} > {self.thresholds['vibration_max']})")
        if cond < self.thresholds["condition_score_min"]:
            risk_triggers.append(f"Degraded Condition Score ({cond:.2f} < {self.thresholds['condition_score_min']})")
        if downtime > self.thresholds["downtime_hours_max"]:
            risk_triggers.append(f"High Downtime ({downtime:.2f} hrs > {self.thresholds['downtime_hours_max']} hrs)")

        is_critical_class = (predicted_label == 2)
        has_telemetry_alarms = (len(risk_triggers) >= 2)
        flag_failure_risk = is_critical_class or has_telemetry_alarms

        if is_critical_class or (has_telemetry_alarms and predicted_label == 1):
            severity = "CRITICAL"
        elif predicted_label == 1 or len(risk_triggers) >= 1:
            severity = "MODERATE"
        else:
            severity = "LOW"

        return {
            "flag_failure_risk": flag_failure_risk,
            "risk_severity": severity,
            "risk_triggers": risk_triggers
        }

    def predict(
        self,
        data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Run end-to-end inference on raw telemetry inputs.

        Args:
            data: Raw DataFrame, dictionary representing a single record,
                  or list of dictionaries.

        Returns:
            List of structured prediction dictionaries.
        """
        # Standardize input to DataFrame
        if isinstance(data, dict):
            raw_df = pd.DataFrame([data])
        elif isinstance(data, list):
            raw_df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            raw_df = data.copy()
        else:
            raise TypeError(f"Unsupported data type for inference: {type(data)}")

        # 1. Feature Engineering
        engineered_df = extract_temporal_features(raw_df)

        # 2. DataFrameMapper Transformation
        transformed = self.mapper.transform(engineered_df)
        if isinstance(transformed, pd.DataFrame):
            x_matrix = transformed.values.astype(np.float32)
        else:
            x_matrix = np.asarray(transformed, dtype=np.float32)

        # 3. ONNX Runtime Inference
        ort_inputs = {self.input_name: x_matrix}
        ort_outputs = self.ort_session.run([self.output_name], ort_inputs)
        probabilities = ort_outputs[0]  # shape: (N, 3)

        results: List[Dict[str, Any]] = []

        for i in range(len(raw_df)):
            probs = probabilities[i].tolist()
            pred_class = int(np.argmax(probs))
            confidence = float(probs[pred_class])
            class_meta = self.label_info.get(pred_class, {
                "name": f"Class {pred_class}",
                "description": "N/A",
                "risk_level": "UNKNOWN"
            })

            # Check risk triggers
            row_series = raw_df.iloc[i]
            asset_id = str(row_series.get("Asset_ID", f"ASSET_{i:04d}"))
            location = str(row_series.get("Location", "Unknown"))
            risk_assessment = self._assess_asset_risk(row_series, pred_class)

            res = {
                "asset_id": asset_id,
                "location": location,
                "predicted_label": pred_class,
                "predicted_class_name": class_meta["name"],
                "confidence": round(confidence, 4),
                "probabilities": {
                    "class_0_optimal": round(probs[0], 4),
                    "class_1_strained": round(probs[1], 4),
                    "class_2_high_risk": round(probs[2], 4)
                },
                "risk_assessment": risk_assessment
            }
            results.append(res)

        return results


def run_verification_suite() -> None:
    """
    Execute comprehensive verification tests:
    1. Multi-class samples extracted from dataset.
    2. Simulated real-time JSON IoT telemetry payload.
    3. Simulated high-risk anomalous asset failure scenario.
    """
    print("\n" + "=" * 75)
    print(">>> FlowCast AI - Module 1: End-to-End Inference Verification Suite")
    print("=" * 75)

    predictor = FlowCastEfficiencyPredictor()

    # Load dataset for representative samples
    df_raw = pd.read_csv(DATA_PATH)

    # Pick samples representing each target label
    sample_indices = []
    for label in [0, 1, 2]:
        matches = df_raw[df_raw["SupplyChain_Efficiency_Label"] == label]
        if not matches.empty:
            sample_indices.append(matches.index[0])

    test_samples = df_raw.iloc[sample_indices].drop(columns=["SupplyChain_Efficiency_Label"])
    actual_labels = df_raw.iloc[sample_indices]["SupplyChain_Efficiency_Label"].tolist()

    print(f"\n--- Test 1: Historical Telemetry Samples (Batch Size: {len(test_samples)}) ---")
    predictions = predictor.predict(test_samples)

    for idx, (res, actual) in enumerate(zip(predictions, actual_labels)):
        print(f"\nSample #{idx + 1} | Asset: {res['asset_id']} | Location: {res['location']}")
        print(f"  Ground Truth Label: {actual}")
        print(f"  Predicted Label:    {res['predicted_label']} ({res['predicted_class_name']})")
        print(f"  Confidence:         {res['confidence'] * 100:.2f}%")
        print(f"  Class Probs:        {res['probabilities']}")
        flag_str = "[FLAGGED - HIGH RISK]" if res['risk_assessment']['flag_failure_risk'] else "[NORMAL]"
        print(f"  Failure Risk Flag:  {flag_str} [{res['risk_assessment']['risk_severity']}]")
        if res['risk_assessment']['risk_triggers']:
            print(f"  Risk Triggers:      {res['risk_assessment']['risk_triggers']}")

    # --- Test 2: Simulated Real-Time JSON Telemetry Payload ---
    print("\n" + "-" * 75)
    print("--- Test 2: Real-Time IoT Telemetry Payload (JSON) ---")
    json_payload = {
        "Asset_ID": "A_STREAM_999",
        "Location": "Rotterdam Gateway Logistics Hub",  # Unseen location test
        "Temperature": 28.5,
        "Vibration": 1.2,
        "Last_Maintenance": "15-08-2024",
        "Condition_Score": 88.5,
        "Resource_Utilization": 82.0,
        "Delivery_Efficiency": 91.5,
        "Downtime_Hours": 1.5,
        "Inventory_Level": "High",
        "Logistics_Cost": 4120.0,
        "Timestamp": "17-10-2024 14:30"
    }
    json_result = predictor.predict(json_payload)[0]
    print(f"Input Payload: {json.dumps(json_payload, indent=2)}")
    print(f"Inference Result:\n{json.dumps(json_result, indent=2)}")

    # --- Test 3: Simulated High-Risk Degradation Edge Case ---
    print("\n" + "-" * 75)
    print("--- Test 3: High-Risk Asset Degradation Anomaly (Stress Test) ---")
    stress_payload = {
        "Asset_ID": "A_CRITICAL_001",
        "Location": "Chicago Cold Storage Terminal",
        "Temperature": 49.8,        # Severe overheating
        "Vibration": 4.95,          # Severe mechanical imbalance
        "Last_Maintenance": "10-01-2023",  # Over 1.5 years without maintenance
        "Condition_Score": 42.0,    # Very poor condition
        "Resource_Utilization": 96.5,
        "Delivery_Efficiency": 62.0,# Poor delivery rate
        "Downtime_Hours": 9.5,      # Excessive downtime
        "Inventory_Level": "Low",
        "Logistics_Cost": 7250.0,
        "Timestamp": "17-10-2024 02:15"
    }
    stress_result = predictor.predict(stress_payload)[0]
    print(f"Stress Payload: {json.dumps(stress_payload, indent=2)}")
    print(f"Inference Result:\n{json.dumps(stress_result, indent=2)}")

    print("\n" + "=" * 75)
    print(">>> All Verification Tests Successfully Executed and Verified!")
    print("=" * 75)


if __name__ == "__main__":
    run_verification_suite()
