"""
FlowCast AI - Production Artifact Serialization.

Handles:
1. Serialization of fitted DataFrameMapper to artifacts/mapper.joblib.
2. Export of trained Deep Learning model to ONNX format at artifacts/model1_efficiency.onnx.
3. Serialization of XGBoost model to artifacts/model_xgb.joblib.
4. Export of pipeline metadata (metrics, feature schema, class mappings) to artifacts/model_metadata.json.
5. ONNX model structure validation and inference sanity check with ONNX Runtime.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import joblib
import numpy as np
import torch
import onnx
import onnxruntime as ort
import xgboost as xgb

from src.config import (
    ARTIFACTS_DIR,
    MAPPER_PATH,
    ONNX_MODEL_PATH,
    XGB_MODEL_PATH,
    METADATA_PATH,
    LABEL_MAPPING,
    CRITICAL_THRESHOLDS,
)
from src.data.preprocess import save_mapper
from src.models.neural_net import AssetHealthEfficiencyNet, ExportableEfficiencyNet
from src.models.train import run_training_pipeline


def export_model_to_onnx(
    model: AssetHealthEfficiencyNet,
    input_dim: int,
    output_path: Optional[Path] = None,
    opset_version: int = 14
) -> Path:
    """
    Export the trained PyTorch neural network to production ONNX format
    with an embedded softmax head for direct probability outputs.

    Args:
        model: Trained AssetHealthEfficiencyNet instance.
        input_dim: Number of input features expected by the model.
        output_path: Destination path for the .onnx file.
        opset_version: ONNX operator set version (default: 14).

    Returns:
        Path to exported ONNX model.
    """
    save_path = Path(output_path) if output_path else ONNX_MODEL_PATH
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Wrap model with Softmax head for ready-to-use probability scores
    export_net = ExportableEfficiencyNet(model)
    export_net.eval()

    dummy_input = torch.randn(1, input_dim, dtype=torch.float32)

    print(f"\nExporting PyTorch model to ONNX: {save_path}...")
    torch.onnx.export(
        export_net,
        dummy_input,
        str(save_path),
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=["telemetry_features"],
        output_names=["probabilities"],
        dynamic_axes={
            "telemetry_features": {0: "batch_size"},
            "probabilities": {0: "batch_size"}
        }
    )

    # 1. Structural check via ONNX
    print("Checking exported ONNX model integrity...")
    onnx_model = onnx.load(str(save_path))
    onnx.checker.check_model(onnx_model)
    print("[OK] ONNX model integrity verified successfully!")

    # 2. Execution check via ONNX Runtime
    print("Verifying execution with ONNX Runtime (CPUExecutionProvider)...")
    session = ort.InferenceSession(str(save_path), providers=["CPUExecutionProvider"])
    ort_inputs = {session.get_inputs()[0].name: dummy_input.numpy()}
    ort_outputs = session.run(None, ort_inputs)
    probs = ort_outputs[0]

    assert probs.shape == (1, 3), f"Unexpected output shape: {probs.shape}"
    assert np.isclose(np.sum(probs), 1.0, atol=1e-4), "Output probabilities do not sum to 1.0"
    print(f"[OK] ONNX Runtime sanity verification passed! Sample test probabilities: {probs}")

    return save_path


def export_all_artifacts() -> Dict[str, Any]:
    """
    Execute full training pipeline and export all production artifacts:
    - artifacts/mapper.joblib
    - artifacts/model1_efficiency.onnx
    - artifacts/model_xgb.joblib
    - artifacts/model_metadata.json

    Returns:
        Dictionary summarizing exported artifacts and evaluation metrics.
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # Train both models and generate full evaluation summary
    xgb_model, nn_model, summary = run_training_pipeline()

    # 1. Export Deep Learning model to ONNX
    input_dim = summary["feature_count"]
    onnx_file = export_model_to_onnx(nn_model, input_dim=input_dim)

    # 2. Export XGBoost model
    print(f"\nSerializing XGBoost model to: {XGB_MODEL_PATH}...")
    joblib.dump(xgb_model, XGB_MODEL_PATH)
    print("[OK] XGBoost baseline serialized successfully!")

    # 3. Export Comprehensive Metadata
    metadata = {
        "project": "FlowCast AI",
        "module": "Module 1: Predictive Asset Health & Operational Efficiency",
        "input_dimension": input_dim,
        "input_features": summary["feature_names"],
        "target_column": "SupplyChain_Efficiency_Label",
        "label_mapping": LABEL_MAPPING,
        "critical_thresholds": CRITICAL_THRESHOLDS,
        "onnx_artifact": str(onnx_file.name),
        "mapper_artifact": str(MAPPER_PATH.name),
        "xgb_artifact": str(XGB_MODEL_PATH.name),
        "evaluation_metrics": {
            "xgboost": summary["xgboost"],
            "neural_network": summary["neural_network"]
        },
        "dataset_split": summary["dataset_split"]
    }

    print(f"Writing pipeline metadata to: {METADATA_PATH}...")
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print("[OK] Pipeline metadata exported successfully!")

    print("\n" + "=" * 60)
    print(">>> All Production Artifacts Successfully Exported:")
    print(f"  1. DataFrameMapper:  {MAPPER_PATH}")
    print(f"  2. ONNX Model:       {ONNX_MODEL_PATH}")
    print(f"  3. XGBoost Model:    {XGB_MODEL_PATH}")
    print(f"  4. Metadata:         {METADATA_PATH}")
    print("=" * 60)

    return metadata


if __name__ == "__main__":
    export_all_artifacts()
