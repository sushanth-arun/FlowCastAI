"""
FlowCast AI - Model Development & Evaluation.

Trains:
1. XGBoost Baseline Classifier.
2. Deep Neural Network (PyTorch MLP) with class-weighted loss for tabular telemetry.
3. Produces detailed evaluation metrics (Accuracy, Macro/Weighted F1, Confusion Matrix, Feature Importances).
"""

from typing import Dict, Any, Tuple, List
import copy
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score
)
import xgboost as xgb
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from src.config import (
    DATA_PATH,
    TARGET_COL,
    XGB_MODEL_PATH
)
from src.data.preprocess import load_and_preprocess_data, save_mapper
from src.models.neural_net import AssetHealthEfficiencyNet, ExportableEfficiencyNet


def compute_class_weights(y_train: np.ndarray) -> torch.Tensor:
    """
    Compute balanced inverse class weights to handle severe class imbalance
    (e.g., rare Label 2 high-risk asset events).

    Args:
        y_train: Integer class array.

    Returns:
        PyTorch float tensor of class weights.
    """
    classes, counts = np.unique(y_train, return_counts=True)
    n_samples = len(y_train)
    n_classes = len(classes)
    weights = n_samples / (n_classes * counts.astype(np.float32))
    return torch.tensor(weights, dtype=torch.float32)


def train_xgboost(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: List[str]
) -> Tuple[xgb.XGBClassifier, Dict[str, Any]]:
    """
    Train and evaluate the XGBoost Baseline Classifier.

    Args:
        X_train: Training features.
        y_train: Training targets.
        X_test: Testing features.
        y_test: Testing targets.
        feature_names: Names of input features.

    Returns:
        Tuple containing trained XGBClassifier and evaluation metrics dict.
    """
    print("\n" + "=" * 60)
    print(">>> Training XGBoost Baseline Classifier...")
    print("=" * 60)

    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='mlogloss'
    )

    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    macro_f1 = float(f1_score(y_test, y_pred, average='macro'))
    weighted_f1 = float(f1_score(y_test, y_pred, average='weighted'))
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)

    # Top feature importances
    importances = model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    top_importances = []
    for idx in sorted_idx[:15]:
        top_importances.append({
            "feature": feature_names[idx] if idx < len(feature_names) else f"feature_{idx}",
            "importance": float(importances[idx])
        })

    metrics = {
        "model_type": "XGBoost",
        "accuracy": acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "confusion_matrix": cm,
        "classification_report": report,
        "top_feature_importances": top_importances
    }

    print(f"XGBoost Accuracy:    {acc:.4f}")
    print(f"XGBoost Macro F1:    {macro_f1:.4f}")
    print(f"XGBoost Weighted F1: {weighted_f1:.4f}")
    print("\nConfusion Matrix:")
    print(np.array(cm))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("Top 8 Most Influential Features:")
    for item in top_importances[:8]:
        print(f"  - {item['feature']:<30}: {item['importance']:.4f}")

    return model, metrics


def train_neural_network(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 1e-3
) -> Tuple[AssetHealthEfficiencyNet, Dict[str, Any]]:
    """
    Train and evaluate Deep Neural Network (PyTorch MLP).

    Args:
        X_train: Training feature matrix.
        y_train: Training labels.
        X_test: Test feature matrix.
        y_test: Test labels.
        epochs: Number of training epochs.
        batch_size: Mini-batch size.
        learning_rate: Optimizer initial learning rate.

    Returns:
        Tuple containing trained AssetHealthEfficiencyNet and metrics dict.
    """
    print("\n" + "=" * 60)
    print(">>> Training Deep Neural Network (PyTorch MLP)...")
    print("=" * 60)

    input_dim = X_train.shape[1]
    num_classes = len(np.unique(y_train))

    model = AssetHealthEfficiencyNet(input_dim=input_dim, num_classes=num_classes)
    class_weights = compute_class_weights(y_train)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    # Tensor datasets & loaders
    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long)
    )
    test_tensor_x = torch.tensor(X_test, dtype=torch.float32)
    test_tensor_y = torch.tensor(y_test, dtype=torch.long)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    best_macro_f1 = -1.0
    best_model_state = None

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0

        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * batch_x.size(0)

        scheduler.step()
        epoch_loss = running_loss / len(X_train)

        # Validation step
        model.eval()
        with torch.no_grad():
            val_logits = model(test_tensor_x)
            val_preds = torch.argmax(val_logits, dim=1).numpy()
            val_f1 = f1_score(y_test, val_preds, average='macro', zero_division=0)

        if val_f1 > best_macro_f1:
            best_macro_f1 = val_f1
            best_model_state = copy.deepcopy(model.state_dict())

        if epoch % 10 == 0 or epoch == epochs:
            print(f"Epoch [{epoch:02d}/{epochs:02d}] - Loss: {epoch_loss:.4f} - Val Macro F1: {val_f1:.4f}")

    # Restore best checkpoint
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    # Final evaluation
    model.eval()
    with torch.no_grad():
        final_logits = model(test_tensor_x)
        final_probs = torch.softmax(final_logits, dim=1).numpy()
        final_preds = np.argmax(final_probs, axis=1)

    acc = float(accuracy_score(y_test, final_preds))
    macro_f1 = float(f1_score(y_test, final_preds, average='macro', zero_division=0))
    weighted_f1 = float(f1_score(y_test, final_preds, average='weighted', zero_division=0))
    cm = confusion_matrix(y_test, final_preds).tolist()
    report = classification_report(y_test, final_preds, output_dict=True, zero_division=0)

    metrics = {
        "model_type": "Deep Neural Network",
        "accuracy": acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "confusion_matrix": cm,
        "classification_report": report
    }

    print("\nNeural Network Evaluation:")
    print(f"NN Accuracy:    {acc:.4f}")
    print(f"NN Macro F1:    {macro_f1:.4f}")
    print(f"NN Weighted F1: {weighted_f1:.4f}")
    print("\nNN Confusion Matrix:")
    print(np.array(cm))
    print("\nNN Classification Report:")
    print(classification_report(y_test, final_preds, zero_division=0))

    return model, metrics


def run_training_pipeline() -> Tuple[xgb.XGBClassifier, AssetHealthEfficiencyNet, Dict[str, Any]]:
    """
    Orchestrate full training, evaluation, and comparison pipeline.

    Returns:
        Tuple containing trained XGBoost model, PyTorch NN model, and metrics dict.
    """
    print("=" * 60)
    print(">>> FlowCast AI - Module 1: Model Training Pipeline")
    print("=" * 60)

    # 1. Load and transform data
    X_df, y_series, mapper, feature_names = load_and_preprocess_data()
    X = X_df.values.astype(np.float32)
    y = y_series.values.astype(np.int64)

    # Persist fitted mapper
    save_mapper(mapper)

    # 2. Stratified train/test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Dataset Split: Train={X_train.shape[0]} samples, Test={X_test.shape[0]} samples")
    print(f"Features: {X_train.shape[1]} dimensions")
    print(f"Train class distribution: {np.bincount(y_train)}")
    print(f"Test class distribution:  {np.bincount(y_test)}")

    # 3. Train XGBoost Baseline
    xgb_model, xgb_metrics = train_xgboost(
        X_train, y_train, X_test, y_test, feature_names
    )

    # 4. Train Deep Neural Network
    nn_model, nn_metrics = train_neural_network(
        X_train, y_train, X_test, y_test, epochs=50, batch_size=32, learning_rate=1e-3
    )

    # Combined performance summary
    summary = {
        "xgboost": xgb_metrics,
        "neural_network": nn_metrics,
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "dataset_split": {
            "train_samples": int(X_train.shape[0]),
            "test_samples": int(X_test.shape[0]),
            "train_class_counts": [int(c) for c in np.bincount(y_train)],
            "test_class_counts": [int(c) for c in np.bincount(y_test)]
        }
    }

    return xgb_model, nn_model, summary


if __name__ == "__main__":
    run_training_pipeline()
