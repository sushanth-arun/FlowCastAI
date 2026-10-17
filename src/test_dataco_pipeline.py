"""
FlowCast AI - Multi-Model Verification Suite.

Validates:
1. Direct ONNX Runtime inference sessions across all 3 modules:
   - artifacts/model1_health.onnx (Asset Health & Operational Efficiency)
   - artifacts/model2_delays.onnx (Logistics & Shipment Delay Risk)
   - artifacts/model3_stock.onnx  (Inventory Demand & Stockout Risk)
2. DataFrameMapper preprocessors for each module.
3. FastAPI Orchestrator Gateway endpoints via TestClient:
   - POST /api/v1/health
   - POST /api/v1/delays
   - POST /api/v1/stockout
   - GET  /healthz
"""

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import onnxruntime as ort
from fastapi.testclient import TestClient

from src.config import (
    ARTIFACTS_DIR,
    MAPPER_PATH,
    ONNX_MODEL_PATH
)
from src.data.preprocess import extract_temporal_features
from src.data.preprocess_dataco import (
    MAPPER_DELAYS_PATH,
    MAPPER_STOCK_PATH,
    parse_dataco_temporal_features
)
from src.api.server import app, ModelManager

MODEL1_HEALTH_PATH = ARTIFACTS_DIR / "model1_health.onnx"
if not MODEL1_HEALTH_PATH.exists() and ONNX_MODEL_PATH.exists():
    MODEL1_HEALTH_PATH = ONNX_MODEL_PATH

MODEL2_DELAYS_PATH = ARTIFACTS_DIR / "model2_delays.onnx"
MODEL3_STOCK_PATH = ARTIFACTS_DIR / "model3_stock.onnx"


def test_direct_onnx_models():
    """
    Directly verify that all 3 ONNX models load into ONNX Runtime,
    accept the expected feature dimensions, and produce valid probability distributions.
    """
    print("\n" + "=" * 70)
    print(">>> Phase 1: Direct ONNX Model Verification (ONNX Runtime)")
    print("=" * 70)

    # 1. Model 1: Asset Health
    print(f"\n[1/3] Testing Module 1 ONNX: {MODEL1_HEALTH_PATH.name}...")
    assert MODEL1_HEALTH_PATH.exists(), f"Missing {MODEL1_HEALTH_PATH}"
    sess1 = ort.InferenceSession(str(MODEL1_HEALTH_PATH), providers=["CPUExecutionProvider"])
    in_dim1 = sess1.get_inputs()[0].shape[1]
    dummy1 = np.random.randn(2, in_dim1).astype(np.float32)
    out1 = sess1.run(None, {sess1.get_inputs()[0].name: dummy1})[0]
    print(f"  Input name: {sess1.get_inputs()[0].name} | Input dimension: {in_dim1}")
    print(f"  Output shape: {out1.shape} | Sample probabilities: {out1[0]}")
    assert out1.shape == (2, 3), f"Unexpected shape {out1.shape}"
    assert np.allclose(np.sum(out1, axis=1), 1.0, atol=1e-3), "Module 1 probabilities must sum to 1"
    print("  [OK] Module 1 (Asset Health) ONNX verification passed!")

    # 2. Model 2: Shipment Delays
    print(f"\n[2/3] Testing Module 2 ONNX: {MODEL2_DELAYS_PATH.name}...")
    assert MODEL2_DELAYS_PATH.exists(), f"Missing {MODEL2_DELAYS_PATH}"
    sess2 = ort.InferenceSession(str(MODEL2_DELAYS_PATH), providers=["CPUExecutionProvider"])
    in_dim2 = sess2.get_inputs()[0].shape[1]
    dummy2 = np.random.randn(2, in_dim2).astype(np.float32)
    out2 = sess2.run(None, {sess2.get_inputs()[0].name: dummy2})[0]
    print(f"  Input name: {sess2.get_inputs()[0].name} | Input dimension: {in_dim2}")
    print(f"  Output shape: {out2.shape} | Sample probabilities: {out2[0]}")
    assert out2.shape == (2, 2), f"Unexpected shape {out2.shape}"
    assert np.allclose(np.sum(out2, axis=1), 1.0, atol=1e-3), "Module 2 probabilities must sum to 1"
    print("  [OK] Module 2 (Logistics Delays) ONNX verification passed!")

    # 3. Model 3: Inventory Stockout
    print(f"\n[3/3] Testing Module 3 ONNX: {MODEL3_STOCK_PATH.name}...")
    assert MODEL3_STOCK_PATH.exists(), f"Missing {MODEL3_STOCK_PATH}"
    sess3 = ort.InferenceSession(str(MODEL3_STOCK_PATH), providers=["CPUExecutionProvider"])
    in_dim3 = sess3.get_inputs()[0].shape[1]
    dummy3 = np.random.randn(2, in_dim3).astype(np.float32)
    out3 = sess3.run(None, {sess3.get_inputs()[0].name: dummy3})[0]
    print(f"  Input name: {sess3.get_inputs()[0].name} | Input dimension: {in_dim3}")
    print(f"  Output shape: {out3.shape} | Sample probabilities: {out3[0]}")
    assert out3.shape == (2, 2), f"Unexpected shape {out3.shape}"
    assert np.allclose(np.sum(out3, axis=1), 1.0, atol=1e-3), "Module 3 probabilities must sum to 1"
    print("  [OK] Module 3 (Inventory Stockout) ONNX verification passed!")


def test_fastapi_gateway():
    """
    Verify all FastAPI orchestrator gateway endpoints using TestClient.
    """
    print("\n" + "=" * 70)
    print(">>> Phase 2: FastAPI Gateway Orchestrator Verification (TestClient)")
    print("=" * 70)

    # Force re-initialization of ModelManager so all artifacts are active
    ModelManager._instance = None
    client = TestClient(app)

    # 1. Healthz
    res_h = client.get("/healthz")
    print("\n[GET /healthz]")
    print(f"Status Code: {res_h.status_code}")
    print(f"Response: {res_h.json()}")
    assert res_h.status_code == 200

    # 2. POST /api/v1/health (Module 1)
    print("\n[POST /api/v1/health] - Testing Telemetry Asset Health...")
    payload_m1 = {
        "Asset_ID": "ASSET_TEST_007",
        "Location": "Rotterdam Gateway Logistics Hub",
        "Temperature": 43.5,
        "Vibration": 4.25,
        "Last_Maintenance": "12-05-2023",
        "Condition_Score": 54.0,
        "Resource_Utilization": 91.0,
        "Delivery_Efficiency": 68.0,
        "Downtime_Hours": 7.5,
        "Inventory_Level": "Medium",
        "Logistics_Cost": 4850.0,
        "Timestamp": "17-10-2024 11:20"
    }
    res_m1 = client.post("/api/v1/health", json=payload_m1)
    print(f"Status Code: {res_m1.status_code}")
    print(f"Response:\n{json.dumps(res_m1.json(), indent=2)}")
    assert res_m1.status_code == 200
    data_m1 = res_m1.json()
    assert "predicted_efficiency_label" in data_m1
    assert "flag_failure_risk" in data_m1

    # 3. POST /api/v1/delays (Module 2)
    print("\n[POST /api/v1/delays] - Testing Logistics Delay Risk...")
    payload_m2 = {
        "Shipping_Mode": "Standard Class",
        "Market": "Pacific Asia",
        "Order_Region": "Southeast Asia",
        "Order_Item_Quantity": 3.0,
        "Sales": 320.0
    }
    res_m2 = client.post("/api/v1/delays", json=payload_m2)
    print(f"Status Code: {res_m2.status_code}")
    print(f"Response:\n{json.dumps(res_m2.json(), indent=2)}")
    assert res_m2.status_code == 200
    data_m2 = res_m2.json()
    assert "late_delivery_risk" in data_m2
    assert "probabilities" in data_m2

    # 4. POST /api/v1/stockout (Module 3)
    print("\n[POST /api/v1/stockout] - Testing Inventory Demand & Stockout Risk...")
    payload_m3 = {
        "Category_Name": "Cardio Equipment",
        "Department_Name": "Fitness",
        "Order_Item_Discount_Rate": 0.15,
        "Product_Price": 149.99
    }
    res_m3 = client.post("/api/v1/stockout", json=payload_m3)
    print(f"Status Code: {res_m3.status_code}")
    print(f"Response:\n{json.dumps(res_m3.json(), indent=2)}")
    assert res_m3.status_code == 200
    data_m3 = res_m3.json()
    assert "stockout_risk_label" in data_m3
    assert "estimated_demand_quantity" in data_m3

    print("\n" + "=" * 70)
    print(">>> All Multi-Model Pipeline & FastAPI Tests Passed Successfully!")
    print("=" * 70)


if __name__ == "__main__":
    test_direct_onnx_models()
    test_fastapi_gateway()
