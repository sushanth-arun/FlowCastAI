"""
FlowCast AI - Module 2 & Module 3 Model Training Pipeline.

Trains:
1. Module 2 (Logistics Delay Risk):
   - XGBoost Classifier predicting Late_delivery_risk (0 or 1).
   - Deep Neural Network (PyTorch MLP) with Softmax head.
   - Evaluates: Accuracy, ROC-AUC, Macro/Weighted F1, Confusion Matrix.
2. Module 3 (Inventory Demand & Stockout Risk):
   - XGBoost Regressor predicting Demand Quantity (Order Item Quantity).
   - XGBoost Classifier predicting Stockout Surge Risk.
   - Deep Neural Network predicting Out-of-Stock Risk probabilities.
   - Evaluates: Demand RMSE, R2, Stockout ROC-AUC, Classification Report.
"""

from typing import Dict, Any, Tuple
import copy
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    f1_score,
    classification_report,
    confusion_matrix,
    mean_squared_error,
    r2_score
)
import xgboost as xgb
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from src.data.preprocess_dataco import (
    load_and_preprocess_dataco,
    save_dataco_mappers
)


# -------------------------------------------------------------
# Neural Network Architectures with Softmax Heads for ONNX
# -------------------------------------------------------------

class DelaysNeuralNet(nn.Module):
    """
    Feedforward Neural Network for predicting Late_delivery_risk (0: On Time, 1: Late).
    """
    def __init__(self, input_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.Mish(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.Mish(),
            nn.Dropout(0.1),
            nn.Linear(32, 2)
        )
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x: torch.Tensor, apply_softmax: bool = False) -> torch.Tensor:
        logits = self.encoder(x)
        if apply_softmax:
            return self.softmax(logits)
        return logits


class StockoutRiskNet(nn.Module):
    """
    Feedforward Neural Network for predicting Stockout / High Demand Risk (0: In Stock, 1: Stockout Risk).
    """
    def __init__(self, input_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.Mish(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.Mish(),
            nn.Dropout(0.1),
            nn.Linear(32, 2)
        )
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x: torch.Tensor, apply_softmax: bool = False) -> torch.Tensor:
        logits = self.encoder(x)
        if apply_softmax:
            return self.softmax(logits)
        return logits


class ExportSoftmaxWrapper(nn.Module):
    """Wrapper that guarantees ONNX model output always applies Softmax."""
    def __init__(self, model: nn.Module):
        super().__init__()
        self.model = model
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = self.model(x, apply_softmax=False)
        return self.softmax(logits)


# -------------------------------------------------------------
# Training Routines
# -------------------------------------------------------------

def train_module2_delays(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    epochs: int = 15
) -> Tuple[xgb.XGBClassifier, DelaysNeuralNet, Dict[str, Any]]:
    """
    Train and evaluate Module 2: Logistics & Shipment Delay Risk.
    """
    print("\n" + "=" * 65)
    print(">>> Training Module 2: Logistics & Shipment Delay Risk Models...")
    print("=" * 65)

    # 1. XGBoost Classifier
    xgb_clf = xgb.XGBClassifier(
        n_estimators=120,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        eval_metric="logloss"
    )
    xgb_clf.fit(X_train, y_train)

    xgb_preds = xgb_clf.predict(X_test)
    xgb_probs = xgb_clf.predict_proba(X_test)[:, 1]
    xgb_auc = float(roc_auc_score(y_test, xgb_probs))
    xgb_acc = float(accuracy_score(y_test, xgb_preds))
    xgb_f1 = float(f1_score(y_test, xgb_preds, average="macro"))

    print(f"XGBoost Delay Accuracy: {xgb_acc:.4f} | ROC-AUC: {xgb_auc:.4f} | Macro F1: {xgb_f1:.4f}")
    print("\nXGBoost Confusion Matrix:")
    print(confusion_matrix(y_test, xgb_preds))
    print("\nXGBoost Classification Report:")
    print(classification_report(y_test, xgb_preds, target_names=["On Time (0)", "Late Delivery (1)"]))

    # 2. Deep Neural Network
    input_dim = X_train.shape[1]
    nn_model = DelaysNeuralNet(input_dim=input_dim)

    # Balanced class weights
    classes, counts = np.unique(y_train, return_counts=True)
    weights = len(y_train) / (len(classes) * counts.astype(np.float32))
    class_weights_t = torch.tensor(weights, dtype=torch.float32)

    criterion = nn.CrossEntropyLoss(weight=class_weights_t)
    optimizer = torch.optim.AdamW(nn_model.parameters(), lr=1e-3, weight_decay=1e-4)

    train_ds = TensorDataset(torch.from_numpy(X_train), torch.tensor(y_train, dtype=torch.long))
    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True)

    test_tensor_x = torch.from_numpy(X_test)
    test_tensor_y = torch.tensor(y_test, dtype=torch.long)

    best_val_auc = 0.0
    best_weights = None

    for epoch in range(1, epochs + 1):
        nn_model.train()
        for bx, by in train_loader:
            optimizer.zero_grad()
            out = nn_model(bx, apply_softmax=False)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()

        # Validation
        nn_model.eval()
        with torch.no_grad():
            val_logits = nn_model(test_tensor_x, apply_softmax=False)
            val_probs = torch.softmax(val_logits, dim=1)[:, 1].numpy()
            val_auc = roc_auc_score(y_test, val_probs)

        if val_auc > best_val_auc:
            best_val_auc = val_auc
            best_weights = copy.deepcopy(nn_model.state_dict())

    if best_weights:
        nn_model.load_state_dict(best_weights)

    # Evaluate final NN
    nn_model.eval()
    with torch.no_grad():
        final_probs = torch.softmax(nn_model(test_tensor_x), dim=1).numpy()
        final_preds = np.argmax(final_probs, axis=1)

    nn_auc = float(roc_auc_score(y_test, final_probs[:, 1]))
    nn_acc = float(accuracy_score(y_test, final_preds))
    nn_f1 = float(f1_score(y_test, final_preds, average="macro"))

    print(f"\nNeural Network Delay Accuracy: {nn_acc:.4f} | ROC-AUC: {nn_auc:.4f} | Macro F1: {nn_f1:.4f}")
    print("\nNN Confusion Matrix:")
    print(confusion_matrix(y_test, final_preds))
    print("\nNN Classification Report:")
    print(classification_report(y_test, final_preds, target_names=["On Time (0)", "Late Delivery (1)"]))

    metrics = {
        "xgboost": {"accuracy": xgb_acc, "roc_auc": xgb_auc, "macro_f1": xgb_f1},
        "neural_network": {"accuracy": nn_acc, "roc_auc": nn_auc, "macro_f1": nn_f1}
    }

    return xgb_clf, nn_model, metrics


def train_module3_stock(
    X_train: np.ndarray,
    y_train_qty: np.ndarray,
    y_train_risk: np.ndarray,
    X_test: np.ndarray,
    y_test_qty: np.ndarray,
    y_test_risk: np.ndarray,
    epochs: int = 15
) -> Tuple[xgb.XGBRegressor, StockoutRiskNet, Dict[str, Any]]:
    """
    Train and evaluate Module 3: Inventory Demand & Stockout Risk.
    """
    print("\n" + "=" * 65)
    print(">>> Training Module 3: Inventory Demand & Stockout Risk Models...")
    print("=" * 65)

    # 1. XGBoost Regressor for Order Item Quantity
    xgb_reg = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        random_state=42
    )
    xgb_reg.fit(X_train, y_train_qty)
    preds_qty = xgb_reg.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test_qty, preds_qty)))
    r2 = float(r2_score(y_test_qty, preds_qty))
    print(f"XGBoost Demand Quantity RMSE: {rmse:.4f} | R2 Score: {r2:.4f}")

    # 2. Deep Neural Network for Out-of-Stock Risk
    input_dim = X_train.shape[1]
    nn_model = StockoutRiskNet(input_dim=input_dim)

    classes, counts = np.unique(y_train_risk, return_counts=True)
    weights = len(y_train_risk) / (len(classes) * counts.astype(np.float32))
    class_weights_t = torch.tensor(weights, dtype=torch.float32)

    criterion = nn.CrossEntropyLoss(weight=class_weights_t)
    optimizer = torch.optim.AdamW(nn_model.parameters(), lr=1e-3, weight_decay=1e-4)

    train_ds = TensorDataset(torch.from_numpy(X_train), torch.tensor(y_train_risk, dtype=torch.long))
    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True)

    test_tensor_x = torch.from_numpy(X_test)

    best_val_auc = 0.0
    best_weights = None

    for epoch in range(1, epochs + 1):
        nn_model.train()
        for bx, by in train_loader:
            optimizer.zero_grad()
            out = nn_model(bx, apply_softmax=False)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()

        nn_model.eval()
        with torch.no_grad():
            val_probs = torch.softmax(nn_model(test_tensor_x), dim=1)[:, 1].numpy()
            val_auc = roc_auc_score(y_test_risk, val_probs)

        if val_auc > best_val_auc:
            best_val_auc = val_auc
            best_weights = copy.deepcopy(nn_model.state_dict())

    if best_weights:
        nn_model.load_state_dict(best_weights)

    nn_model.eval()
    with torch.no_grad():
        final_probs = torch.softmax(nn_model(test_tensor_x), dim=1).numpy()
        final_preds = np.argmax(final_probs, axis=1)

    nn_auc = float(roc_auc_score(y_test_risk, final_probs[:, 1]))
    nn_acc = float(accuracy_score(y_test_risk, final_preds))
    nn_f1 = float(f1_score(y_test_risk, final_preds, average="macro"))

    print(f"\nNeural Network Stockout Risk Accuracy: {nn_acc:.4f} | ROC-AUC: {nn_auc:.4f} | Macro F1: {nn_f1:.4f}")
    print("\nNN Stockout Confusion Matrix:")
    print(confusion_matrix(y_test_risk, final_preds))
    print("\nNN Stockout Classification Report:")
    print(classification_report(y_test_risk, final_preds, target_names=["In Stock / Normal (0)", "Stockout Risk (1)"]))

    metrics = {
        "demand_regression": {"rmse": rmse, "r2": r2},
        "stockout_risk_nn": {"accuracy": nn_acc, "roc_auc": nn_auc, "macro_f1": nn_f1}
    }

    return xgb_reg, nn_model, metrics


def run_full_dataco_training(
    sample_size: int = 40000
) -> Tuple[
    xgb.XGBClassifier, DelaysNeuralNet,
    xgb.XGBRegressor, StockoutRiskNet,
    Any, Any, Dict[str, Any]
]:
    """
    Run full training for both Module 2 and Module 3 on DataCo Supply Chain Dataset.
    """
    df, y_delays, y_demand, y_stockout_risk, mapper_delays, mapper_stock = load_and_preprocess_dataco(
        sample_size=sample_size
    )

    save_dataco_mappers(mapper_delays, mapper_stock)

    # 1. Transform Module 2 Features
    X_delays = mapper_delays.transform(df).values.astype(np.float32)
    y_delays_arr = y_delays.values.astype(np.int64)

    X_train_del, X_test_del, y_train_del, y_test_del = train_test_split(
        X_delays, y_delays_arr, test_size=0.20, random_state=42, stratify=y_delays_arr
    )

    xgb_del, nn_del, metrics_del = train_module2_delays(
        X_train_del, y_train_del, X_test_del, y_test_del, epochs=15
    )

    # 2. Transform Module 3 Features
    X_stock = mapper_stock.transform(df).values.astype(np.float32)
    y_demand_arr = y_demand.values.astype(np.float32)
    y_stockout_arr = y_stockout_risk.values.astype(np.int64)

    X_train_stk, X_test_stk, y_train_qty, y_test_qty, y_train_stk, y_test_stk = train_test_split(
        X_stock, y_demand_arr, y_stockout_arr, test_size=0.20, random_state=42, stratify=y_stockout_arr
    )

    xgb_stk, nn_stk, metrics_stk = train_module3_stock(
        X_train_stk, y_train_qty, y_train_stk,
        X_test_stk, y_test_qty, y_test_stk,
        epochs=15
    )

    summary = {
        "module2_delays": metrics_del,
        "module3_stock": metrics_stk,
        "delays_input_dim": int(X_delays.shape[1]),
        "stock_input_dim": int(X_stock.shape[1]),
        "delays_features": list(mapper_delays.transformed_names_),
        "stock_features": list(mapper_stock.transformed_names_)
    }

    return xgb_del, nn_del, xgb_stk, nn_stk, mapper_delays, mapper_stock, summary


if __name__ == "__main__":
    run_full_dataco_training(sample_size=35000)
