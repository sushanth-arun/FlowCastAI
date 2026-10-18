"""
FlowCast AI - Multi-Model FastAPI Orchestrator Gateway.

Exposes endpoints:
1. POST /api/v1/health   - Module 1: Predictive Asset Health & Operational Efficiency (ONNX)
2. POST /api/v1/delays   - Module 2: Logistics & Shipment Delay Risk (ONNX)
3. POST /api/v1/stockout - Module 3: Inventory Demand & Stockout Risk (ONNX)
4. GET  /healthz         - Service Health & Active ONNX Sessions status
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
try:
    import onnxruntime as ort
except ImportError:
    ort = None
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.models.inference_engine import UniversalInferenceSession

from src.config import (
    ARTIFACTS_DIR,
    MAPPER_PATH,
    ONNX_MODEL_PATH,
    LABEL_MAPPING,
    CRITICAL_THRESHOLDS
)
from src.data.preprocess import extract_temporal_features
from src.data.preprocess_dataco import (
    MAPPER_DELAYS_PATH,
    MAPPER_STOCK_PATH,
    parse_dataco_temporal_features
)
from src.api.dashboard import DASHBOARD_HTML
from src.models.recovery_engine import FlowCastNetworkEngine

MODEL1_HEALTH_ONNX = ARTIFACTS_DIR / "model1_health.onnx"
if not MODEL1_HEALTH_ONNX.exists() and ONNX_MODEL_PATH.exists():
    MODEL1_HEALTH_ONNX = ONNX_MODEL_PATH

MODEL2_DELAYS_ONNX = ARTIFACTS_DIR / "model2_delays.onnx"
MODEL3_STOCK_ONNX = ARTIFACTS_DIR / "model3_stock.onnx"
XGB_STOCK_PATH = ARTIFACTS_DIR / "model_xgb_stock.joblib"
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


# -------------------------------------------------------------
# Request & Response Schemas
# -------------------------------------------------------------

class AssetHealthRequest(BaseModel):
    Asset_ID: str = Field(default="A0001", description="Asset identifier")
    Location: str = Field(default="Lake Davidland", description="Operational facility location")
    Temperature: float = Field(default=32.34, description="Operating temperature in Celsius")
    Vibration: float = Field(default=3.99, description="Vibration frequency/amplitude metric")
    Last_Maintenance: str = Field(default="28-09-2023", description="Date of last service (DD-MM-YYYY)")
    Condition_Score: float = Field(default=67.39, description="Asset structural condition score (0-100)")
    Resource_Utilization: float = Field(default=87.04, description="Workload capacity percentage (0-100)")
    Delivery_Efficiency: float = Field(default=79.99, description="Throughput delivery efficiency (0-100)")
    Downtime_Hours: float = Field(default=3.22, description="Cumulative unscheduled downtime hours")
    Inventory_Level: str = Field(default="Medium", description="Inventory stock level: Low, Medium, High")
    Logistics_Cost: float = Field(default=5148.45, description="Associated logistics expenditure ($)")
    Timestamp: str = Field(default="13-09-2024 19:31", description="Event timestamp (DD-MM-YYYY HH:MM)")


class AssetHealthResponse(BaseModel):
    asset_id: str
    location: str
    predicted_efficiency_label: int
    classification_name: str
    confidence: float
    probabilities: Dict[str, float]
    flag_failure_risk: bool
    risk_severity: str
    risk_triggers: List[str]


class DelayRiskRequest(BaseModel):
    Shipping_Mode: str = Field(default="Standard Class", description="Shipping Mode: Standard Class, First Class, Second Class, Same Day")
    Market: str = Field(default="LATAM", description="Global Market destination: Pacific Asia, USCA, Africa, Europe, LATAM")
    Order_Region: str = Field(default="South America", description="World Order Region")
    Order_Item_Quantity: float = Field(default=2.0, description="Number of items ordered")
    Sales: float = Field(default=250.0, description="Gross order sales volume ($)")
    Days_for_shipping_real: Optional[float] = Field(default=None, description="Actual days taken if known")
    Days_for_shipment_scheduled: Optional[float] = Field(default=4.0, description="Target scheduled delivery days")


class DelayRiskResponse(BaseModel):
    late_delivery_risk: int
    delay_prediction_label: str
    confidence: float
    probabilities: Dict[str, float]
    delay_severity: str


class StockoutRequest(BaseModel):
    Category_Name: str = Field(default="Cardio Equipment", description="Product category description")
    Department_Name: str = Field(default="Fitness", description="Store department name")
    Order_Item_Discount_Rate: float = Field(default=0.10, description="Discount rate applied (0.0 - 1.0)")
    Product_Price: float = Field(default=129.99, description="Retail product price ($)")
    Product_Name: Optional[str] = Field(default=None, description="Optional product name")


class StockoutResponse(BaseModel):
    stockout_risk_label: int
    stockout_risk_status: str
    confidence: float
    probabilities: Dict[str, float]
    estimated_demand_quantity: float
    inventory_action_recommendation: str


# -------------------------------------------------------------
# Gateway Application & Model Manager
# -------------------------------------------------------------

app = FastAPI(
    title="FlowCast AI - Intelligent Supply Chain Decision Support Gateway",
    version="2.0.0",
    description="Multi-model ONNX runtime service for Asset Health, Logistics Delays, and Inventory Stockout Prediction."
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModelManager:
    """Manages lazy-loaded ONNX runtime / universal NumPy inference sessions and preprocessors."""
    _instance = None

    def __init__(self):
        self.sessions: Dict[str, Any] = {}
        self.mappers: Dict[str, Any] = {}
        self.xgb_models: Dict[str, Any] = {}
        self._init_models()

    def _init_models(self):
        # Session options optimized for high-throughput enterprise execution
        opts = None
        if ort is not None:
            opts = ort.SessionOptions()
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            opts.intra_op_num_threads = 4

        weights_dict = {}
        np_weights_path = ARTIFACTS_DIR / "model_weights_numpy.joblib"
        if np_weights_path.exists():
            try:
                weights_dict = joblib.load(np_weights_path)
            except Exception:
                pass

        # 1. Module 1: Asset Health
        if MAPPER_PATH.exists():
            self.mappers["health"] = joblib.load(MAPPER_PATH)
        health_model = MODEL1_HEALTH_ONNX if MODEL1_HEALTH_ONNX.exists() else ONNX_MODEL_PATH
        self.sessions["health"] = UniversalInferenceSession(
            "health",
            health_model if health_model.exists() else None,
            weights_dict.get("health"),
            opts
        )

        # 2. Module 2: Logistics Delays
        if MAPPER_DELAYS_PATH.exists():
            self.mappers["delays"] = joblib.load(MAPPER_DELAYS_PATH)
        self.sessions["delays"] = UniversalInferenceSession(
            "delays",
            MODEL2_DELAYS_ONNX if MODEL2_DELAYS_ONNX.exists() else None,
            weights_dict.get("delays"),
            opts
        )

        # 3. Module 3: Stockout & Demand
        if MAPPER_STOCK_PATH.exists():
            self.mappers["stock"] = joblib.load(MAPPER_STOCK_PATH)
        self.sessions["stock"] = UniversalInferenceSession(
            "stock",
            MODEL3_STOCK_ONNX if MODEL3_STOCK_ONNX.exists() else None,
            weights_dict.get("stock"),
            opts
        )
        if XGB_STOCK_PATH.exists():
            try:
                self.xgb_models["stock_demand"] = joblib.load(XGB_STOCK_PATH)
            except Exception:
                pass

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._instance


# -------------------------------------------------------------
# Static Assets & Endpoints
# -------------------------------------------------------------

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


@app.get("/", response_class=HTMLResponse, summary="FlowCast AI Modern React Dashboard")
def serve_dashboard():
    """Serve the modern React frontend application for FlowCast AI."""
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse(content=DASHBOARD_HTML, status_code=200)


@app.get("/legacy", response_class=HTMLResponse, summary="FlowCast AI Prototype Dashboard")
def serve_legacy_dashboard():
    """Fallback interactive prototype dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML, status_code=200)


@app.get("/favicon.svg", include_in_schema=False)
def serve_favicon():
    fav = FRONTEND_DIST / "favicon.svg"
    if fav.exists():
        return FileResponse(str(fav))
    return HTMLResponse(content="", status_code=404)


@app.get("/icons.svg", include_in_schema=False)
def serve_icons():
    ico = FRONTEND_DIST / "icons.svg"
    if ico.exists():
        return FileResponse(str(ico))
    return HTMLResponse(content="", status_code=404)


@app.get("/healthz", summary="System Health Status")
def healthz():
    mgr = ModelManager.get_instance()
    return {
        "status": "healthy",
        "service": "FlowCast AI Multi-Model Gateway",
        "loaded_sessions": list(mgr.sessions.keys()),
        "loaded_mappers": list(mgr.mappers.keys())
    }


@app.get("/api/v1/network/state", summary="Get 3-Warehouse Network Inventory & Disruption State")
def get_network_state(scenario: str = "scenario_1", warehouse: Optional[str] = "ALL"):
    """
    Returns complete multi-warehouse network state, inventory balances,
    active inbound shipment risks, and calculated recovery optimization plans.
    """
    valid_scenarios = ["scenario_1", "scenario_2", "scenario_3", "scenario_4"]
    if scenario not in valid_scenarios:
        scenario = "scenario_1"
    
    state = FlowCastNetworkEngine.get_network_state(
        scenario_id=scenario,
        selected_wh_id=warehouse
    )
    return state


@app.post("/api/v1/network/recovery", summary="Evaluate Custom Recovery Options")
def evaluate_network_recovery(scenario: str = "scenario_2"):
    """
    Runs multi-warehouse recovery optimization solver across all three hubs.
    """
    warehouses = FlowCastNetworkEngine.get_base_scenario(scenario)
    recovery_plan = FlowCastNetworkEngine.evaluate_recovery(warehouses)
    return recovery_plan


@app.post("/api/v1/health", response_model=AssetHealthResponse, summary="Predict Asset Health & Operational Efficiency")
def predict_asset_health(req: AssetHealthRequest):
    mgr = ModelManager.get_instance()
    if "health" not in mgr.sessions or "health" not in mgr.mappers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Module 1 (Asset Health) model or mapper not loaded."
        )

    # Convert request to DataFrame matching training schema
    raw_dict = {
        "Asset_ID": req.Asset_ID,
        "Location": req.Location,
        "Temperature": req.Temperature,
        "Vibration": req.Vibration,
        "Last_Maintenance": req.Last_Maintenance,
        "Condition_Score": req.Condition_Score,
        "Resource_Utilization": req.Resource_Utilization,
        "Delivery_Efficiency": req.Delivery_Efficiency,
        "Downtime_Hours": req.Downtime_Hours,
        "Inventory_Level": req.Inventory_Level,
        "Logistics_Cost": req.Logistics_Cost,
        "Timestamp": req.Timestamp
    }
    df_raw = pd.DataFrame([raw_dict])

    # Feature transformation
    df_engineered = extract_temporal_features(df_raw)
    x_matrix = mgr.mappers["health"].transform(df_engineered)
    if isinstance(x_matrix, pd.DataFrame):
        x_matrix = x_matrix.values.astype(np.float32)
    else:
        x_matrix = np.asarray(x_matrix, dtype=np.float32)

    # ONNX Inference
    session = mgr.sessions["health"]
    input_name = session.get_inputs()[0].name
    probs = session.run(None, {input_name: x_matrix})[0][0]

    pred_label = int(np.argmax(probs))
    conf = float(probs[pred_label])
    meta = LABEL_MAPPING.get(pred_label, {"name": f"Class {pred_label}", "risk_level": "UNKNOWN"})

    # Threshold checks
    triggers = []
    if req.Temperature > CRITICAL_THRESHOLDS["temperature_max"]:
        triggers.append(f"Temperature high: {req.Temperature:.1f}C")
    if req.Vibration > CRITICAL_THRESHOLDS["vibration_max"]:
        triggers.append(f"Vibration high: {req.Vibration:.2f}")
    if req.Condition_Score < CRITICAL_THRESHOLDS["condition_score_min"]:
        triggers.append(f"Condition score degraded: {req.Condition_Score:.1f}")
    if req.Downtime_Hours > CRITICAL_THRESHOLDS["downtime_hours_max"]:
        triggers.append(f"Downtime excessive: {req.Downtime_Hours:.1f} hrs")

    flag_risk = (pred_label == 2) or (len(triggers) >= 2)
    severity = "CRITICAL" if flag_risk else ("MODERATE" if pred_label == 1 else "LOW")

    return AssetHealthResponse(
        asset_id=req.Asset_ID,
        location=req.Location,
        predicted_efficiency_label=pred_label,
        classification_name=meta["name"],
        confidence=round(conf, 4),
        probabilities={
            "class_0_optimal": round(float(probs[0]), 4),
            "class_1_strained": round(float(probs[1]), 4),
            "class_2_high_risk": round(float(probs[2]), 4)
        },
        flag_failure_risk=flag_risk,
        risk_severity=severity,
        risk_triggers=triggers
    )


@app.post("/api/v1/delays", response_model=DelayRiskResponse, summary="Predict Logistics & Shipment Delay Risk")
def predict_shipment_delay(req: DelayRiskRequest):
    mgr = ModelManager.get_instance()
    if "delays" not in mgr.sessions or "delays" not in mgr.mappers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Module 2 (Delay Risk) model or mapper not loaded."
        )

    raw_dict = {
        "Shipping Mode": req.Shipping_Mode,
        "Market": req.Market,
        "Order Region": req.Order_Region,
        "Order Item Quantity": req.Order_Item_Quantity,
        "Sales": req.Sales
    }
    df_raw = pd.DataFrame([raw_dict])

    x_matrix = mgr.mappers["delays"].transform(df_raw)
    if isinstance(x_matrix, pd.DataFrame):
        x_matrix = x_matrix.values.astype(np.float32)
    else:
        x_matrix = np.asarray(x_matrix, dtype=np.float32)

    session = mgr.sessions["delays"]
    input_name = session.get_inputs()[0].name
    probs = session.run(None, {input_name: x_matrix})[0][0]

    pred_label = int(np.argmax(probs))
    conf = float(probs[pred_label])
    prob_delay = float(probs[1])

    delay_name = "LATE_DELIVERY_RISK" if pred_label == 1 else "ON_TIME"
    severity = "HIGH" if prob_delay >= 0.70 else ("MODERATE" if prob_delay >= 0.50 else "LOW")

    return DelayRiskResponse(
        late_delivery_risk=pred_label,
        delay_prediction_label=delay_name,
        confidence=round(conf, 4),
        probabilities={
            "on_time_prob": round(float(probs[0]), 4),
            "late_risk_prob": round(float(probs[1]), 4)
        },
        delay_severity=severity
    )


@app.post("/api/v1/stockout", response_model=StockoutResponse, summary="Predict Inventory Demand & Stockout Risk")
def predict_stockout_risk(req: StockoutRequest):
    mgr = ModelManager.get_instance()
    if "stock" not in mgr.sessions or "stock" not in mgr.mappers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Module 3 (Stockout Risk) model or mapper not loaded."
        )

    raw_dict = {
        "Category Name": req.Category_Name,
        "Department Name": req.Department_Name,
        "Order Item Discount Rate": req.Order_Item_Discount_Rate,
        "Product Price": req.Product_Price
    }
    df_raw = pd.DataFrame([raw_dict])

    x_matrix = mgr.mappers["stock"].transform(df_raw)
    if isinstance(x_matrix, pd.DataFrame):
        x_matrix = x_matrix.values.astype(np.float32)
    else:
        x_matrix = np.asarray(x_matrix, dtype=np.float32)

    # 1. ONNX Stockout Surge Risk Session
    session = mgr.sessions["stock"]
    input_name = session.get_inputs()[0].name
    probs = session.run(None, {input_name: x_matrix})[0][0]

    pred_label = int(np.argmax(probs))
    conf = float(probs[pred_label])

    # 2. XGBoost Demand Regressor estimation (if available)
    est_demand = 2.5
    if "stock_demand" in mgr.xgb_models:
        est_demand = float(mgr.xgb_models["stock_demand"].predict(x_matrix)[0])
        est_demand = round(max(1.0, est_demand), 2)

    risk_status = "ELEVATED_STOCKOUT_RISK" if pred_label == 1 else "IN_STOCK_STABLE"
    recommendation = (
        "Trigger immediate replenishment order; demand surge probability is high."
        if pred_label == 1 else
        "Inventory levels within safe operational thresholds."
    )

    return StockoutResponse(
        stockout_risk_label=pred_label,
        stockout_risk_status=risk_status,
        confidence=round(conf, 4),
        probabilities={
            "stable_stock_prob": round(float(probs[0]), 4),
            "stockout_risk_prob": round(float(probs[1]), 4)
        },
        estimated_demand_quantity=est_demand,
        inventory_action_recommendation=recommendation
    )


if __name__ == "__main__":
    import uvicorn
    print("Launching FlowCast AI FastAPI Orchestrator Gateway...")
    print("Live Server:           http://148.100.108.248:8000/")
    print("Swagger OpenAPI Docs:  http://148.100.108.248:8000/docs")
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
