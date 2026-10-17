"""
FlowCast AI - Deep Neural Network Architecture.

Implements multi-layer feedforward architecture with batch normalization,
regularization (dropout), non-linear activations, and export-ready softmax head.
"""

from typing import Tuple
import torch
import torch.nn as nn


class AssetHealthEfficiencyNet(nn.Module):
    """
    Multi-Layer Perceptron (MLP) for predicting Supply Chain Efficiency labels (0, 1, 2)
    from scaled continuous telemetry and encoded categorical indicators.
    """

    def __init__(self, input_dim: int, num_classes: int = 3, hidden_dims: Tuple[int, ...] = (128, 64, 32)):
        """
        Initialize network architecture.

        Args:
            input_dim: Number of input features from DataFrameMapper.
            num_classes: Number of efficiency classification categories (default: 3).
            hidden_dims: Tuple specifying hidden layer dimensions.
        """
        super().__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes

        layers = []
        in_features = input_dim

        for idx, h_dim in enumerate(hidden_dims):
            layers.append(nn.Linear(in_features, h_dim))
            layers.append(nn.BatchNorm1d(h_dim))
            layers.append(nn.Mish())
            # Progressive dropout to avoid overfitting on tabular telemetry
            dropout_rate = 0.25 if idx == 0 else (0.20 if idx == 1 else 0.10)
            layers.append(nn.Dropout(dropout_rate))
            in_features = h_dim

        layers.append(nn.Linear(in_features, num_classes))
        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass producing unnormalized class logits.

        Args:
            x: Input tensor of shape (batch_size, input_dim).

        Returns:
            Logits tensor of shape (batch_size, num_classes).
        """
        return self.network(x)


class ExportableEfficiencyNet(nn.Module):
    """
    Inference-ready wrapper that includes Softmax probability activation
    for clean production ONNX runtime export.
    """

    def __init__(self, base_model: AssetHealthEfficiencyNet):
        super().__init__()
        self.base_model = base_model
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass yielding normalized confidence probabilities.

        Args:
            x: Input feature tensor (batch_size, input_dim).

        Returns:
            Probabilities tensor (batch_size, num_classes) summing to 1.0.
        """
        logits = self.base_model(x)
        return self.softmax(logits)
