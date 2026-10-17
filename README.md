# FlowCast AI: Intelligent Multi-Echelon Supply-Chain Decision Support System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX-Runtime-green.svg)](https://onnxruntime.ai/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Gateway-009688.svg)](https://fastapi.tiangolo.com/)
[![IBM Z Datathon](https://img.shields.io/badge/IBM%20Z-Datathon%202026-brightgreen.svg)](https://www.ibm.com/community/z/)

FlowCast AI is an end-to-end operational decision-support and proactive disruption recovery system designed to predict logistical bottlenecks, asset degradation, and stockout surges across interconnected multi-warehouse supply chain networks.

---

## 🌟 Key Capabilities

1. **Module 1: Predictive Asset Health & Telemetry Analytics**
   - Ingests IoT telemetry (temperature, vibration, downtime hours, condition score).
   - Classifies equipment operational state into 3 distinct efficiency tiers (`Optimal`, `Sub-Optimal/Strained`, `High Risk Degradation`).
   - Flags critical physical anomalies before catastrophic failures occur.

2. **Module 2: Logistics & Shipment Delay Risk Forecasting**
   - Trained on historical logistics and order transit data from the DataCo Supply Chain dataset.
   - Evaluates scheduled vs. real transit patterns to predict late delivery risks (`ON_TIME` vs `LATE_RISK`).

3. **Module 3: Inventory Demand & Stockout Surge Risk**
   - Dual-head predictive engine combining continuous demand quantity regression (XGBoost) and categorical stockout surge classification (Deep Neural Network exported to ONNX).

4. **3-Warehouse Decision Support & Recovery Optimization Engine**
   - Interconnected network across 3 major logistical hubs:
     - **Warehouse A (Chennai - WH-A)**: Maritime / Port gateway.
     - **Warehouse B (Bengaluru - WH-B)**: Inland technology and distribution hub.
     - **Warehouse C (Hyderabad - WH-C)**: Central distribution hub.
   - **Cost & Shortage-Based Recovery Solver**: Automatically computes optimal inter-warehouse stock rebalancing and expedited replenishment transfers during disruptions while strictly protecting source safety stock buffers and preventing double-allocation of surplus stock.

---

## 📊 Model Performance Benchmarks

All models are serialized and served via high-performance **ONNX Runtime** inference sessions:

| Module | Architecture | Input Dims | Accuracy | ROC-AUC / F1 | Artifact |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Module 1: Asset Health** | Deep Neural Network (Softmax) | 528 | **87.00%** | Macro F1: **0.8032** | `artifacts/model1_health.onnx` |
| **Module 1 (Auxiliary)** | XGBoost Classifier | 528 | **97.00%** | Macro F1: **0.8717** | `artifacts/model_xgb.joblib` |
| **Module 2: Logistics Delays** | Deep Neural Network | 34 | **71.66%** | ROC-AUC: **0.7627** | `artifacts/model2_delays.onnx` |
| **Module 2 (Auxiliary)** | XGBoost Classifier | 34 | **71.73%** | ROC-AUC: **0.7612** | `artifacts/model_xgb_delays.joblib` |
| **Module 3: Stockout Risk** | Stockout Risk Neural Net | 55 | **62.71%** | ROC-AUC: **0.7401** (99.2% recall) | `artifacts/model3_stock.onnx` |
| **Module 3: Demand Regressor**| XGBoost Regressor | 55 | RMSE: **1.176** | $R^2$: **0.4229** | `artifacts/model_xgb_stock.joblib` |

---

## 🚀 Quickstart & Installation

### 1. Prerequisites & Virtual Environment
```bash
git clone https://github.com/sushanth-arun/FlowCastAI.git
cd FlowCastAI

# Create and activate python virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate # Linux/macOS
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn onnxruntime torch xgboost scikit-learn sklearn-pandas pandas numpy
```

### 3. Launch FastAPI Orchestrator Gateway
```bash
python -m src.api.server
```
The server will start at:
- **Interactive Decision Control Center**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive OpenAPI (Swagger) Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint**: [http://localhost:8000/healthz](http://localhost:8000/healthz)

---

## 🔌 API Reference

### Health Check
- `GET /healthz`: Returns loaded ONNX sessions and feature mappers.

### Multi-Warehouse Decision Support
- `GET /api/v1/network/state?scenario={scenario_id}&warehouse={ALL|WH-A|WH-B|WH-C}`: Dynamic multi-warehouse state, inventory balances, disruption flags, and recovery plans.
- `POST /api/v1/network/recovery?scenario={scenario_id}`: Triggers the optimization recovery solver across hubs.

### Machine Learning Inference
- `POST /api/v1/health`: Real-time asset health classification and physical anomaly detection.
- `POST /api/v1/delays`: Logistics delay risk forecasting.
- `POST /api/v1/stockout`: Demand estimation and stockout surge risk classification.

---

## 🧪 Running Verification Tests
Execute the comprehensive test suites to verify end-to-end functionality:
```bash
python -m src.test_dataco_pipeline
python -m src.test_3wh_system
python -m src.inference_test
```

---

## 📁 Repository Structure
```
├── artifacts/                  # Serialized ONNX models, mappers, and metadata
│   ├── model1_health.onnx
│   ├── model2_delays.onnx
│   ├── model3_stock.onnx
│   ├── mapper.joblib
│   ├── mapper_delays.joblib
│   └── mapper_stock.joblib
├── data/                       # Normalized supply chain datasets
│   ├── bdt_mba_supplychain_dataset_2024.csv
│   └── DescriptionDataCoSupplyChain.csv
├── src/
│   ├── api/                    # FastAPI gateway and interactive dashboard
│   │   ├── server.py
│   │   └── dashboard.py
│   ├── data/                   # Feature engineering and temporal parsing
│   │   ├── preprocess.py
│   │   └── preprocess_dataco.py
│   └── models/                 # Model architectures, training, & recovery engine
│       ├── recovery_engine.py
│       ├── neural_net.py
│       ├── train.py
│       └── export_dataco.py
└── .gitignore
```
