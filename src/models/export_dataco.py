"""
FlowCast AI - DataCo Production Artifact Serialization.

Handles:
1. Serialization of DataFrameMappers:
   - artifacts/mapper_delays.joblib
   - artifacts/mapper_stock.joblib
2. ONNX export of deep neural models:
   - artifacts/model2_delays.onnx
   - artifacts/model3_stock.onnx
3. Harmonizing artifacts/model1_health.onnx (alias for model1_efficiency.onnx).
4. Validation and ONNX Runtime execution verification.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import shutil
import json
import joblib
import numpy as np
import torch
import onnx
import onnxruntime as ort

from src.config import ARTIFACTS_DIR, ONNX_MODEL_PATH
from src.data.preprocess_dataco import (
    MAPPER_DELAYS_PATH,
    MAPPER_STOCK_PATH,
    save_dataco_mappers
)
from src.models.train_dataco import (
    run_full_dataco_training,
    ExportSoftmaxWrapper,
    DelaysNeuralNet,
    StockoutRiskNet
)

MODEL2_DELAYS_ONNX: Path = ARTIFACTS_DIR / "model2_delays.onnx"
MODEL3_STOCK_ONNX: Path = ARTIFACTS_DIR / "model3_stock.onnx"
MODEL1_HEALTH_ONNX: Path = ARTIFACTS_DIR / "model1_health.onnx"
DATACO_METADATA_PATH: Path = ARTIFACTS_DIR / "dataco_metadata.json"
XGB_DELAYS_PATH: Path = ARTIFACTS_DIR / "model_xgb_delays.joblib"
XGB_STOCK_PATH: Path = ARTIFACTS_DIR / "model_xgb_stock.joblib"


def export_torch_to_onnx(
    model: torch.nn.Module,
    input_dim: int,
    output_path: Path,
    input_name: str,
    output_name: str
) -> Path:
    """
    Export PyTorch model wrapped with Softmax head to ONNX format.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wrapped = ExportSoftmaxWrapper(model)
    wrapped.eval()

    dummy_input = torch.randn(1, input_dim, dtype=torch.float32)

    print(f"Exporting ONNX model to: {output_path} (input dim: {input_dim})...")
    torch.onnx.export(
        wrapped,
        dummy_input,
        str(output_path),
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=[input_name],
        output_names=[output_name],
        dynamic_axes={
            input_name: {0: "batch_size"},
            output_name: {0: "batch_size"}
        }
    )

    # 1. Structural check
    onnx_m = onnx.load(str(output_path))
    onnx.checker.check_model(onnx_m)
    print(f"[OK] ONNX structural verification passed: {output_path.name}")

    # 2. Execution check via ONNX Runtime
    session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
    ort_in = {session.get_inputs()[0].name: dummy_input.numpy()}
    ort_out = session.run(None, ort_in)[0]

    assert ort_out.shape == (1, 2), f"Expected shape (1, 2), got {ort_out.shape}"
    assert np.isclose(np.sum(ort_out), 1.0, atol=1e-4), "Probabilities must sum to 1.0"
    print(f"[OK] ONNX Runtime test passed! Output probabilities: {ort_out}")

    return output_path


def export_all_dataco_artifacts(sample_size: int = 35000) -> Dict[str, Any]:
    """
    Execute full DataCo training pipeline, export ONNX models, and save metadata.
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print(">>> FlowCast AI: Training & Exporting Module 2 and Module 3...")
    print("=" * 65)

    (
        xgb_del, nn_del,
        xgb_stk, nn_stk,
        mapper_delays, mapper_stock,
        summary
    ) = run_full_dataco_training(sample_size=sample_size)

    # 1. Save DataFrameMappers
    save_dataco_mappers(mapper_delays, mapper_stock)
    print(f"[OK] Saved mappers to:\n  - {MAPPER_DELAYS_PATH}\n  - {MAPPER_STOCK_PATH}")

    # 2. Export Module 2 ONNX Model
    export_torch_to_onnx(
        model=nn_del,
        input_dim=summary["delays_input_dim"],
        output_path=MODEL2_DELAYS_ONNX,
        input_name="logistics_features",
        output_name="delay_probabilities"
    )

    # 3. Export Module 3 ONNX Model
    export_torch_to_onnx(
        model=nn_stk,
        input_dim=summary["stock_input_dim"],
        output_path=MODEL3_STOCK_ONNX,
        input_name="stock_features",
        output_name="stockout_probabilities"
    )

    # 4. Serialize XGBoost models
    joblib.dump(xgb_del, XGB_DELAYS_PATH)
    joblib.dump(xgb_stk, XGB_STOCK_PATH)
    print(f"[OK] Serialized XGBoost models to:\n  - {XGB_DELAYS_PATH}\n  - {XGB_STOCK_PATH}")

    # 5. Verify model1_health.onnx
    if ONNX_MODEL_PATH.exists() and ONNX_MODEL_PATH != MODEL1_HEALTH_ONNX:
        shutil.copyfile(ONNX_MODEL_PATH, MODEL1_HEALTH_ONNX)
    if MODEL1_HEALTH_ONNX.exists():
        print(f"[OK] Verified active artifact: {MODEL1_HEALTH_ONNX.name}")

    # 6. Save metadata
    with open(DATACO_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[OK] Saved metadata to: {DATACO_METADATA_PATH}")

    print("\n" + "=" * 65)
    print(">>> All Module 2 & Module 3 Artifacts Exported Successfully!")
    print("=" * 65)

    return summary


if __name__ == "__main__":
    export_all_dataco_artifacts()
